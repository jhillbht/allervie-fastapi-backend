import logging
import traceback
from datetime import datetime, timedelta
import yaml
import pytz
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from app.core.config import GOOGLE_ADS_YAML_PATH, ENVIRONMENT

# Set up logging
logger = logging.getLogger(__name__)

class GoogleAdsService:
    """Service for interacting with the Google Ads API."""
    
    @staticmethod
    def get_google_ads_client():
        """
        Creates and returns a Google Ads API client.
        
        Returns:
            GoogleAdsClient: Configured client for Google Ads API
            None: If client creation fails
        """
        try:
            # Try different API versions if the configured one fails
            yaml_path = str(GOOGLE_ADS_YAML_PATH)
            logger.info(f"Loading Google Ads client from: {yaml_path}")
            
            # Explicitly check and print YAML file contents (without sensitive info)
            try:
                with open(yaml_path, 'r') as yaml_file:
                    config = yaml.safe_load(yaml_file)
                    # Log some non-sensitive info to verify file is loaded correctly
                    logger.info(f"YAML config contains login_customer_id: {config.get('login_customer_id', 'Not Found')}")
                    logger.info(f"YAML config contains api_version: {config.get('api_version', 'Not Found')}")
                    logger.info(f"YAML config contains use_proto_plus: {config.get('use_proto_plus', 'Not Found')}")
                    
                    # Verify required fields
                    required_fields = ['client_id', 'client_secret', 'developer_token', 'login_customer_id', 'refresh_token']
                    missing_fields = [field for field in required_fields if not config.get(field)]
                    if missing_fields:
                        error_msg = f"Missing required fields in google-ads.yaml: {missing_fields}"
                        logger.error(error_msg)
                        
                        if ENVIRONMENT == "production":
                            raise ValueError(error_msg)
                        return None
                        
            except Exception as yaml_error:
                logger.error(f"Error reading YAML file: {yaml_error}")
                if ENVIRONMENT == "production":
                    raise
                return None
            
            # Load the client with the API version from the YAML file
            api_version = config.get('api_version', 'v13')
            
            try:
                client = GoogleAdsClient.load_from_storage(yaml_path, version=api_version)
                logger.info(f"Successfully loaded Google Ads client with API version {api_version}")
                
                # Test if the client has the necessary methods
                if not hasattr(client, 'get_service'):
                    error_msg = "Client missing required 'get_service' method"
                    logger.error(error_msg)
                    return None
                
                return client
            except Exception as e:
                logger.error(f"Failed to create client with API version {api_version}: {e}")
                
                # Fall back to try alternative versions
                fallback_versions = ['v13', 'v12', 'v11']
                for version in fallback_versions:
                    if version == api_version:
                        continue  # Skip if it's the same as the one we just tried
                    try:
                        logger.info(f"Trying fallback to API version {version}")
                        client = GoogleAdsClient.load_from_storage(yaml_path, version=version)
                        if client and hasattr(client, 'get_service'):
                            logger.info(f"Fallback to {version} successful!")
                            return client
                    except Exception:
                        continue  # Try next version
                        
                logger.error("All fallback version attempts failed")
                return None
        except Exception as e:
            logger.error(f"Error getting Google Ads client: {e}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    async def get_ads_performance(start_date=None, end_date=None, previous_period=False):
        """
        Fetches performance metrics from Google Ads API for the specified date range.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to 30 days ago.
            end_date (str, optional): End date in YYYY-MM-DD format. Defaults to yesterday.
            previous_period (bool, optional): If True, fetch data for the previous
                period of the same length and calculate percentage changes. Defaults to False.
        
        Returns:
            dict: Performance metrics with values and percentage changes
            None: If the request fails
        """
        # Get Google Ads client
        client = GoogleAdsService.get_google_ads_client()
        if not client:
            logger.error("Failed to create Google Ads client")
            return None
        
        # Set default date range if not provided
        today = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not end_date:
            # Default to yesterday
            end_date_obj = today - timedelta(days=1)
            end_date = end_date_obj.strftime('%Y-%m-%d')
        else:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            except ValueError:
                logger.error(f"Invalid end date format: {end_date}. Must be YYYY-MM-DD")
                return None
        
        if not start_date:
            # Default to 30 days ago
            start_date_obj = today - timedelta(days=30)
            start_date = start_date_obj.strftime('%Y-%m-%d')
        else:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            except ValueError:
                logger.error(f"Invalid start date format: {start_date}. Must be YYYY-MM-DD")
                return None
        
        logger.info(f"Fetching Google Ads performance data for period: {start_date} to {end_date}")
        
        # Calculate previous period date range if requested
        if previous_period:
            period_length = (end_date_obj - start_date_obj).days
            prev_end_date_obj = start_date_obj - timedelta(days=1)
            prev_start_date_obj = prev_end_date_obj - timedelta(days=period_length)
            prev_start_date = prev_start_date_obj.strftime('%Y-%m-%d')
            prev_end_date = prev_end_date_obj.strftime('%Y-%m-%d')
            logger.info(f"Will also fetch previous period: {prev_start_date} to {prev_end_date}")
        
        try:
            # Get the customer ID from config
            customer_id = client.login_customer_id
            
            # Create Google Ads query
            query = f"""
                SELECT 
                    metrics.impressions, 
                    metrics.clicks, 
                    metrics.conversions, 
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.all_conversions_from_interactions_rate,
                    metrics.cost_per_conversion
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            logger.debug(f"Query: {query}")
            
            # Get the service and execute query
            ga_service = client.get_service("GoogleAdsService")
            if not ga_service:
                logger.error("Failed to get GoogleAdsService")
                return None
                
            logger.info("Successfully got GoogleAdsService")
            
            # Execute the query with proper error handling
            try:
                search_response = ga_service.search(
                    customer_id=customer_id,
                    query=query
                )
                logger.info("Successfully executed search query")
            except GoogleAdsException as google_ads_error:
                logger.error(f"Google Ads API error: {google_ads_error}")
                return None
            except Exception as e:
                logger.error(f"Error executing search query: {e}")
                return None
            
            # Process the response
            total_impressions = 0
            total_clicks = 0
            total_conversions = 0
            total_cost_micros = 0
            total_weighted_ctr = 0
            total_weighted_conv_rate = 0
            total_weighted_cost_per_conv = 0
            
            # Process each row in the response
            for row in search_response:
                metrics = row.metrics
                total_impressions += metrics.impressions
                total_clicks += metrics.clicks
                total_conversions += metrics.conversions
                total_cost_micros += metrics.cost_micros
                
                # Calculate weighted rate metrics
                if metrics.impressions > 0:
                    total_weighted_ctr += metrics.ctr * metrics.impressions
                if metrics.clicks > 0:
                    total_weighted_conv_rate += metrics.all_conversions_from_interactions_rate * metrics.clicks
                if metrics.conversions > 0:
                    total_weighted_cost_per_conv += metrics.cost_per_conversion * metrics.conversions
            
            # Calculate averages and format metrics
            avg_ctr = (total_weighted_ctr / total_impressions) if total_impressions > 0 else 0
            avg_conv_rate = (total_weighted_conv_rate / total_clicks) if total_clicks > 0 else 0
            avg_cost_per_conv = (total_weighted_cost_per_conv / total_conversions) if total_conversions > 0 else 0
            total_cost = total_cost_micros / 1_000_000  # Convert micros to actual currency
            
            # Format the response with only real data from the API
            current_period_data = {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "cost": total_cost,
                "clickThroughRate": avg_ctr,
                "conversionRate": avg_conv_rate,
                "costPerConversion": avg_cost_per_conv
            }
            
            # If previous period data is requested, fetch it
            if previous_period:
                prev_query = query.replace(start_date, prev_start_date).replace(end_date, prev_end_date)
                try:
                    prev_response = ga_service.search(
                        customer_id=customer_id,
                        query=prev_query
                    )
                    
                    # Process previous period data
                    prev_metrics = {
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "cost_micros": 0,
                        "weighted_ctr": 0,
                        "weighted_conv_rate": 0,
                        "weighted_cost_per_conv": 0
                    }
                    
                    for row in prev_response:
                        metrics = row.metrics
                        prev_metrics["impressions"] += metrics.impressions
                        prev_metrics["clicks"] += metrics.clicks
                        prev_metrics["conversions"] += metrics.conversions
                        prev_metrics["cost_micros"] += metrics.cost_micros
                        
                        if metrics.impressions > 0:
                            prev_metrics["weighted_ctr"] += metrics.ctr * metrics.impressions
                        if metrics.clicks > 0:
                            prev_metrics["weighted_conv_rate"] += metrics.all_conversions_from_interactions_rate * metrics.clicks
                        if metrics.conversions > 0:
                            prev_metrics["weighted_cost_per_conv"] += metrics.cost_per_conversion * metrics.conversions
                    
                    # Calculate percentage changes
                    def calc_change(current, previous):
                        if previous == 0:
                            return 0 if current == 0 else 100
                        return ((current - previous) / previous) * 100
                    
                    result = {
                        "impressions": {
                            "value": current_period_data["impressions"],
                            "change": calc_change(current_period_data["impressions"], prev_metrics["impressions"])
                        },
                        "clicks": {
                            "value": current_period_data["clicks"],
                            "change": calc_change(current_period_data["clicks"], prev_metrics["clicks"])
                        },
                        "conversions": {
                            "value": current_period_data["conversions"],
                            "change": calc_change(current_period_data["conversions"], prev_metrics["conversions"])
                        },
                        "cost": {
                            "value": current_period_data["cost"],
                            "change": calc_change(current_period_data["cost"], prev_metrics["cost_micros"] / 1_000_000)
                        },
                        "clickThroughRate": {
                            "value": current_period_data["clickThroughRate"],
                            "change": calc_change(current_period_data["clickThroughRate"], 
                                               (prev_metrics["weighted_ctr"] / prev_metrics["impressions"]) if prev_metrics["impressions"] > 0 else 0)
                        },
                        "conversionRate": {
                            "value": current_period_data["conversionRate"],
                            "change": calc_change(current_period_data["conversionRate"], 
                                               (prev_metrics["weighted_conv_rate"] / prev_metrics["clicks"]) if prev_metrics["clicks"] > 0 else 0)
                        },
                        "costPerConversion": {
                            "value": current_period_data["costPerConversion"],
                            "change": calc_change(current_period_data["costPerConversion"],
                                               (prev_metrics["weighted_cost_per_conv"] / prev_metrics["conversions"]) if prev_metrics["conversions"] > 0 else 0)
                        }
                    }
                except Exception as prev_error:
                    logger.error(f"Error fetching previous period data: {prev_error}")
                    # Return current period data without changes if previous period fails
                    result = {metric: {"value": value, "change": 0} 
                             for metric, value in current_period_data.items()}
            else:
                # Return current period data without changes
                result = {metric: {"value": value, "change": 0} 
                         for metric, value in current_period_data.items()}
            
            logger.info("Successfully processed Google Ads performance data")
            return result
            
        except Exception as e:
            logger.error(f"Error processing Google Ads performance data: {e}")
            logger.error(traceback.format_exc())
            return None

    @staticmethod
    async def get_campaigns():
        """Fetch Google Ads campaign data"""
        # Get Google Ads client
        client = GoogleAdsService.get_google_ads_client()
        if not client:
            logger.error("Failed to create Google Ads client")
            return None
            
        try:
            # Get the customer ID from config
            customer_id = client.login_customer_id
            
            # Create query for campaigns
            query = """
                SELECT 
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.conversions_from_interactions_rate,
                    metrics.cost_per_conversion
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY metrics.impressions DESC
            """
            
            # Get the service and execute query
            ga_service = client.get_service("GoogleAdsService")
            
            # Execute the query
            search_response = ga_service.search(
                customer_id=customer_id,
                query=query
            )
            
            # Process results
            campaigns = []
            for row in search_response:
                campaign = row.campaign
                metrics = row.metrics
                
                campaigns.append({
                    "id": campaign.id.value,
                    "name": campaign.name.value,
                    "status": str(campaign.status.name),
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "conversions": metrics.conversions,
                    "cost": metrics.cost_micros / 1_000_000,
                    "ctr": metrics.ctr * 100,  # Convert to percentage
                    "conversion_rate": metrics.conversions_from_interactions_rate * 100,  # Convert to percentage
                    "costPerConversion": metrics.cost_per_conversion
                })
            
            logger.info(f"Successfully retrieved {len(campaigns)} campaigns")
            return campaigns
            
        except Exception as e:
            logger.error(f"Error fetching campaigns: {e}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    async def get_ad_groups(campaign_id=None):
        """Fetch Google Ads ad group data"""
        # Get Google Ads client
        client = GoogleAdsService.get_google_ads_client()
        if not client:
            logger.error("Failed to create Google Ads client")
            return None
            
        try:
            # Get the customer ID from config
            customer_id = client.login_customer_id
            
            # Build the query
            query = """
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    ad_group.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.conversions_from_interactions_rate,
                    metrics.cost_per_conversion
                FROM ad_group
                WHERE ad_group.status != 'REMOVED'
            """
            
            # Add campaign filter if provided
            if campaign_id:
                query += f" AND campaign.id = {campaign_id}"
                
            query += " ORDER BY metrics.impressions DESC"
            
            # Get the service and execute query
            ga_service = client.get_service("GoogleAdsService")
            
            # Execute the query
            search_response = ga_service.search(
                customer_id=customer_id,
                query=query
            )
            
            # Process results
            ad_groups = []
            for row in search_response:
                ad_group = row.ad_group
                campaign = row.campaign
                metrics = row.metrics
                
                ad_groups.append({
                    "id": ad_group.id.value,
                    "name": ad_group.name.value,
                    "campaign_id": campaign.id.value,
                    "campaign_name": campaign.name.value,
                    "status": str(ad_group.status.name),
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "conversions": metrics.conversions,
                    "cost": metrics.cost_micros / 1_000_000,
                    "ctr": metrics.ctr * 100,  # Convert to percentage
                    "conversion_rate": metrics.conversions_from_interactions_rate * 100,  # Convert to percentage
                    "costPerConversion": metrics.cost_per_conversion
                })
            
            logger.info(f"Successfully retrieved {len(ad_groups)} ad groups")
            return ad_groups
            
        except Exception as e:
            logger.error(f"Error fetching ad groups: {e}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    async def get_search_terms(campaign_id=None):
        """Fetch Google Ads search term data"""
        # Get Google Ads client
        client = GoogleAdsService.get_google_ads_client()
        if not client:
            logger.error("Failed to create Google Ads client")
            return None
            
        try:
            # Get the customer ID from config
            customer_id = client.login_customer_id
            
            # Build the query
            query = """
                SELECT 
                    search_term_view.search_term,
                    campaign.id,
                    campaign.name,
                    ad_group.id,
                    ad_group.name,
                    search_term_view.status,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros,
                    metrics.ctr,
                    metrics.conversions_from_interactions_rate,
                    metrics.cost_per_conversion,
                    ad_group_criterion.keyword.match_type
                FROM search_term_view
            """
            
            # Add campaign filter if provided
            if campaign_id:
                query += f" WHERE campaign.id = {campaign_id}"
                
            query += " ORDER BY metrics.impressions DESC LIMIT 100"
            
            # Get the service and execute query
            ga_service = client.get_service("GoogleAdsService")
            
            # Execute the query
            search_response = ga_service.search(
                customer_id=customer_id,
                query=query
            )
            
            # Process results
            search_terms = []
            for row in search_response:
                search_term = row.search_term_view.search_term.value
                campaign = row.campaign
                match_type = row.ad_group_criterion.keyword.match_type.name
                metrics = row.metrics
                
                search_terms.append({
                    "search_term": search_term,
                    "campaign_id": campaign.id.value,
                    "campaign_name": campaign.name.value,
                    "match_type": str(match_type),
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "conversions": metrics.conversions,
                    "cost": metrics.cost_micros / 1_000_000,
                    "ctr": metrics.ctr * 100,  # Convert to percentage
                    "conversion_rate": metrics.conversions_from_interactions_rate * 100,  # Convert to percentage
                    "costPerConversion": metrics.cost_per_conversion
                })
            
            logger.info(f"Successfully retrieved {len(search_terms)} search terms")
            return search_terms
            
        except Exception as e:
            logger.error(f"Error fetching search terms: {e}")
            logger.error(traceback.format_exc())
            return None
