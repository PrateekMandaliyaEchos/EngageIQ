"""Profile Generator Agent - Analyzes segments and generates comprehensive agent profiles."""

import pandas as pd
from typing import Dict, Any, List
from collections import Counter

from src.agents.base_agent import BaseAgent, Message
from src.core.config import get_settings
from src.llm import ClaudeProvider


class ProfileGeneratorAgent(BaseAgent):
    """
    Profile Generator Agent that analyzes segmented agents and generates comprehensive profiles.
    
    Responsibilities:
    1. Analyze the filtered agent segment
    2. Compute detailed statistics (avg AUM, NPS distribution, etc.)
    3. Generate segment description using LLM
    4. Return comprehensive profile summary
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize profile generator agent.
        
        Args:
            config: Agent configuration from config.yaml
        """
        settings = get_settings()
        agent_config = settings.get_agent_config('profiler')
        super().__init__("ProfileGeneratorAgent", agent_config)
        
        self.settings = settings
        
        # Get LLM provider configuration
        llm_provider_name = agent_config.get('provider', settings.llm_default_provider)
        llm_config = settings.get_llm_config(llm_provider_name)
        
        # Override temperature if specified in agent config
        if 'temperature' in agent_config:
            llm_config['temperature'] = agent_config['temperature']
        
        # Initialize LLM provider
        self.llm = ClaudeProvider(llm_config)
        
    def process(self, message: Message) -> Dict[str, Any]:
        """
        Generate comprehensive profile for segmented agents.
        
        Args:
            message: Message containing segmentation results and agent data
            
        Returns:
            Dictionary with comprehensive profile analysis
        """
        try:
            # Extract segmentation results and agent data
            segmentation_results = message.content.get('segmentation', {})
            agent_data = message.content.get('agent_data', {})
            criteria = message.content.get('criteria', {})
            
            if not segmentation_results.get('success'):
                raise ValueError("No valid segmentation results provided")
            
            # Get filtered agent data - use all_filtered for profile generation
            filtered_agents = segmentation_results.get('all_filtered', [])
            agent_ids = segmentation_results.get('agent_ids', [])
            
            if not filtered_agents:
                raise ValueError("No filtered agents to profile")
            
            # Convert to DataFrame for analysis
            agent_df = pd.DataFrame(filtered_agents)
            
            # Compute detailed statistics
            statistics = self._compute_detailed_statistics(agent_df)
            
            # Generate segment insights
            insights = self._generate_segment_insights(agent_df, criteria)
            
            # Generate LLM-powered segment description
            segment_description = self._generate_segment_description(
                agent_df, criteria, statistics, insights
            )
            
            # Generate individual agent profiles
            agent_profiles = self._generate_agent_profiles(agent_df)

            # Generate segment-specific breakdowns
            segments_breakdown = self._generate_segments_breakdown(agent_df, criteria, statistics)

            return {
                "success": True,
                "segment_summary": {
                    "total_agents": len(agent_df),
                    "agent_ids": agent_ids,
                    "objective": criteria.get('objective', 'unknown'),
                    "criteria_applied": criteria.get('constraints', [])
                },
                "statistics": statistics,
                "insights": insights,
                "segment_description": segment_description,
                "agent_profiles": agent_profiles,
                "segments_breakdown": segments_breakdown,
                "recommendations": self._generate_recommendations(statistics, insights, criteria)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Profile generation failed: {str(e)}",
                "segment_summary": {},
                "statistics": {},
                "insights": {},
                "segment_description": "",
                "agent_profiles": []
            }
    
    def _compute_detailed_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute detailed statistics for the agent segment.
        
        Args:
            df: DataFrame of filtered agents
            
        Returns:
            Dictionary with comprehensive statistics
        """
        stats = {}
        
        # Financial metrics
        if 'AUM_SELFREPORTED' in df.columns:
            aum_data = pd.to_numeric(df['AUM_SELFREPORTED'], errors='coerce')
            stats['aum'] = {
                "count": int(aum_data.count()),
                "mean": float(aum_data.mean()) if not aum_data.empty and pd.notna(aum_data.mean()) else 0,
                "median": float(aum_data.median()) if not aum_data.empty and pd.notna(aum_data.median()) else 0,
                "std": float(aum_data.std()) if not aum_data.empty and pd.notna(aum_data.std()) else 0,
                "min": float(aum_data.min()) if not aum_data.empty and pd.notna(aum_data.min()) else 0,
                "max": float(aum_data.max()) if not aum_data.empty and pd.notna(aum_data.max()) else 0,
                "q25": float(aum_data.quantile(0.25)) if not aum_data.empty and pd.notna(aum_data.quantile(0.25)) else 0,
                "q75": float(aum_data.quantile(0.75)) if not aum_data.empty and pd.notna(aum_data.quantile(0.75)) else 0
            }
        
        # Satisfaction metrics
        if 'NPS_SCORE' in df.columns:
            nps_data = pd.to_numeric(df['NPS_SCORE'], errors='coerce')
            stats['nps'] = {
                "count": int(nps_data.count()),
                "mean": float(nps_data.mean()) if not nps_data.empty and pd.notna(nps_data.mean()) else 0,
                "median": float(nps_data.median()) if not nps_data.empty and pd.notna(nps_data.median()) else 0,
                "distribution": dict(Counter(nps_data.dropna().astype(int))),
                "promoters": int((nps_data >= 9).sum()),
                "passives": int(((nps_data >= 7) & (nps_data <= 8)).sum()),
                "detractors": int((nps_data <= 6).sum())
            }
        
        # Tenure metrics
        if 'AGENT_TENURE' in df.columns:
            tenure_data = pd.to_numeric(df['AGENT_TENURE'], errors='coerce')
            stats['tenure'] = {
                "count": int(tenure_data.count()),
                "mean": float(tenure_data.mean()) if not tenure_data.empty and pd.notna(tenure_data.mean()) else 0,
                "median": float(tenure_data.median()) if not tenure_data.empty and pd.notna(tenure_data.median()) else 0,
                "min": float(tenure_data.min()) if not tenure_data.empty and pd.notna(tenure_data.min()) else 0,
                "max": float(tenure_data.max()) if not tenure_data.empty and pd.notna(tenure_data.max()) else 0,
                "distribution": {
                    "new": int((tenure_data < 2).sum()),
                    "experienced": int(((tenure_data >= 2) & (tenure_data < 5)).sum()),
                    "veteran": int((tenure_data >= 5).sum())
                }
            }
        
        # Performance metrics
        if 'NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS' in df.columns:
            sales_data = pd.to_numeric(df['NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS'], errors='coerce')
            stats['sales_performance'] = {
                "count": int(sales_data.count()),
                "mean": float(sales_data.mean()) if not sales_data.empty and pd.notna(sales_data.mean()) else 0,
                "median": float(sales_data.median()) if not sales_data.empty and pd.notna(sales_data.median()) else 0,
                "total_policies": int(sales_data.sum()) if not sales_data.empty and pd.notna(sales_data.sum()) else 0,
                "distribution": {
                    "low": int((sales_data < 5).sum()),
                    "medium": int(((sales_data >= 5) & (sales_data < 15)).sum()),
                    "high": int((sales_data >= 15).sum())
                }
            }
        
        # Demographics
        if 'Segment' in df.columns:
            stats['demographics'] = {
                "segments": dict(Counter(df['Segment'].dropna())),
                "total_segments": len(df['Segment'].unique())
            }
        
        if 'Age' in df.columns:
            age_data = pd.to_numeric(df['Age'], errors='coerce')
            stats['demographics']['age'] = {
                "mean": float(age_data.mean()) if not age_data.empty and pd.notna(age_data.mean()) else 0,
                "median": float(age_data.median()) if not age_data.empty and pd.notna(age_data.median()) else 0,
                "distribution": {
                    "young": int((age_data < 35).sum()),
                    "middle": int(((age_data >= 35) & (age_data < 55)).sum()),
                    "senior": int((age_data >= 55).sum())
                }
            }
        
        return stats
    
    def _generate_segment_insights(self, df: pd.DataFrame, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights about the segment characteristics.
        
        Args:
            df: DataFrame of filtered agents
            criteria: Applied criteria
            
        Returns:
            Dictionary with segment insights
        """
        insights = {
            "segment_characteristics": [],
            "key_findings": [],
            "opportunities": []
        }
        
        # Analyze segment characteristics
        if len(df) > 0:
            insights["segment_characteristics"].append(f"Segment size: {len(df)} agents")
            
            # AUM insights
            if 'AUM_SELFREPORTED' in df.columns:
                avg_aum = df['AUM_SELFREPORTED'].mean()
                insights["segment_characteristics"].append(f"Average AUM: ${avg_aum:,.0f}")
                
                if avg_aum > 5000000:
                    insights["key_findings"].append("High-value agent segment with premium AUM")
                elif avg_aum > 2000000:
                    insights["key_findings"].append("Mid-to-high value agent segment")
                else:
                    insights["key_findings"].append("Standard value agent segment")
            
            # NPS insights
            if 'NPS_SCORE' in df.columns:
                avg_nps = df['NPS_SCORE'].mean()
                insights["segment_characteristics"].append(f"Average NPS: {avg_nps:.1f}")
                
                if avg_nps >= 8:
                    insights["key_findings"].append("High satisfaction segment - strong retention potential")
                    insights["opportunities"].append("Focus on loyalty programs and premium services")
                elif avg_nps >= 6:
                    insights["key_findings"].append("Moderate satisfaction segment - improvement opportunity")
                    insights["opportunities"].append("Implement satisfaction improvement initiatives")
                else:
                    insights["key_findings"].append("Low satisfaction segment - high churn risk")
                    insights["opportunities"].append("Urgent intervention needed for retention")
            
            # Tenure insights
            if 'AGENT_TENURE' in df.columns:
                avg_tenure = df['AGENT_TENURE'].mean()
                insights["segment_characteristics"].append(f"Average tenure: {avg_tenure:.1f} years")
                
                if avg_tenure >= 5:
                    insights["key_findings"].append("Veteran agent segment with deep experience")
                elif avg_tenure >= 2:
                    insights["key_findings"].append("Experienced agent segment")
                else:
                    insights["key_findings"].append("New agent segment requiring support")
        
        return insights
    
    def _generate_segment_description(self, df: pd.DataFrame, criteria: Dict[str, Any], 
                                     statistics: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """
        Generate LLM-powered segment description.
        
        Args:
            df: DataFrame of filtered agents
            criteria: Applied criteria
            statistics: Computed statistics
            insights: Generated insights
            
        Returns:
            LLM-generated segment description
        """
        # Prepare data summary for LLM
        data_summary = {
            "segment_size": len(df),
            "criteria": criteria,
            "key_statistics": {
                "avg_aum": statistics.get('aum', {}).get('mean', 0),
                "avg_nps": statistics.get('nps', {}).get('mean', 0),
                "avg_tenure": statistics.get('tenure', {}).get('mean', 0),
                "total_sales": statistics.get('sales_performance', {}).get('total_policies', 0)
            },
            "insights": insights
        }
        
        prompt = f"""
        Analyze this insurance agent segment and provide a comprehensive description:
        
        SEGMENT DATA:
        - Size: {data_summary['segment_size']} agents
        - Objective: {criteria.get('objective', 'unknown')}
        - Criteria Applied: {criteria.get('constraints', [])}
        
        KEY STATISTICS:
        - Average AUM: ${data_summary['key_statistics']['avg_aum']:,.0f}
        - Average NPS Score: {data_summary['key_statistics']['avg_nps']:.1f}
        - Average Tenure: {data_summary['key_statistics']['avg_tenure']:.1f} years
        - Total Policies Sold: {data_summary['key_statistics']['total_sales']}
        
        INSIGHTS:
        {insights.get('key_findings', [])}
        
        Please provide a comprehensive 2-3 paragraph description that:
        1. Summarizes the segment characteristics
        2. Highlights key strengths and opportunities
        3. Provides strategic recommendations for campaign targeting
        
        Focus on actionable insights for marketing and retention strategies.
        """
        
        try:
            description = self.llm.query(
                prompt=prompt,
                system="You are an expert insurance marketing analyst specializing in agent segmentation and campaign strategy."
            )
            return description
        except Exception as e:
            return f"Segment analysis: {len(df)} agents meeting criteria with average AUM of ${data_summary['key_statistics']['avg_aum']:,.0f} and NPS of {data_summary['key_statistics']['avg_nps']:.1f}. {insights.get('key_findings', ['Standard segment characteristics'])[0]}."
    
    def _generate_agent_profiles(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate individual agent profiles.
        
        Args:
            df: DataFrame of filtered agents
            
        Returns:
            List of individual agent profiles
        """
        profiles = []
        
        for _, agent in df.iterrows():
            profile = {
                "agent_id": agent.get('AGENT_ID', 'Unknown'),
                "name": f"{agent.get('AGENT_FIRST_NAME', '')} {agent.get('AGENT_LAST_NAME', '')}".strip(),
                "segment": agent.get('Segment', 'Unknown'),
                "aum": float(agent.get('AUM_SELFREPORTED', 0)) if pd.notna(agent.get('AUM_SELFREPORTED')) else 0,
                "nps_score": float(agent.get('NPS_SCORE', 0)) if pd.notna(agent.get('NPS_SCORE')) else 0,
                "tenure": float(agent.get('AGENT_TENURE', 0)) if pd.notna(agent.get('AGENT_TENURE')) else 0,
                "policies_sold": int(agent.get('NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS', 0)) if pd.notna(agent.get('NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS')) else 0,
                "age": int(agent.get('Age', 0)) if pd.notna(agent.get('Age')) else 0,
                "city": agent.get('CITY', 'Unknown'),
                "education": agent.get('EDUCATION', 'Unknown'),
                "premium_amount": float(agent.get('PREMIUM_AMOUNT', 0)) if pd.notna(agent.get('PREMIUM_AMOUNT')) else 0,
                "nps_feedback": agent.get('NPS_FEEDBACK', 'No feedback available')
            }
            profiles.append(profile)
        
        return profiles
    
    def _generate_recommendations(self, statistics: Dict[str, Any], insights: Dict[str, Any], 
                                criteria: Dict[str, Any]) -> List[str]:
        """
        Generate strategic recommendations based on analysis.
        
        Args:
            statistics: Computed statistics
            insights: Generated insights
            criteria: Applied criteria
            
        Returns:
            List of strategic recommendations
        """
        recommendations = []
        
        # AUM-based recommendations
        avg_aum = statistics.get('aum', {}).get('mean', 0)
        if avg_aum > 5000000:
            recommendations.append("Premium service tier: Offer exclusive high-value agent benefits")
            recommendations.append("Wealth management focus: Target sophisticated financial products")
        elif avg_aum > 2000000:
            recommendations.append("Growth opportunity: Upsell premium products and services")
        
        # NPS-based recommendations
        avg_nps = statistics.get('nps', {}).get('mean', 0)
        if avg_nps >= 8:
            recommendations.append("Retention focus: Maintain high satisfaction with loyalty programs")
            recommendations.append("Advocacy program: Leverage promoters for referrals and testimonials")
        elif avg_nps < 6:
            recommendations.append("Urgent intervention: Implement satisfaction recovery program")
            recommendations.append("Root cause analysis: Investigate specific pain points")
        
        # Tenure-based recommendations
        avg_tenure = statistics.get('tenure', {}).get('mean', 0)
        if avg_tenure >= 5:
            recommendations.append("Mentorship program: Leverage veteran agents to train newcomers")
            recommendations.append("Legacy recognition: Acknowledge long-term relationships")
        elif avg_tenure < 2:
            recommendations.append("Onboarding enhancement: Strengthen new agent support programs")
            recommendations.append("Early success focus: Provide additional training and resources")
        
        # Objective-based recommendations
        objective = criteria.get('objective', '')
        if objective == 'retention':
            recommendations.append("Retention campaign: Focus on loyalty and satisfaction improvement")
        elif objective == 'acquisition':
            recommendations.append("Acquisition campaign: Target similar high-potential agents")
        elif objective == 'upsell':
            recommendations.append("Upsell campaign: Introduce premium products to existing relationships")

        return recommendations[:5]  # Limit to top 5 recommendations

    def _generate_segments_breakdown(self, df: pd.DataFrame, criteria: Dict[str, Any],
                                     overall_statistics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate segment-specific breakdowns for each customer segment.

        Segments: Independent Agents, Emerging Experts, Accomplished Professionals, Comfortable Retirees

        Args:
            df: Filtered agent DataFrame
            criteria: Campaign criteria
            overall_statistics: Overall statistics for all agents

        Returns:
            Dictionary with per-segment profiles and statistics
        """
        segments_breakdown = {}

        if 'Segment' not in df.columns or df.empty:
            return segments_breakdown

        # Group by Segment
        for segment_name, segment_df in df.groupby('Segment'):
            if segment_df.empty:
                continue

            segment_breakdown = {
                "segment_name": segment_name,
                "agent_count": len(segment_df),
                "percentage_of_total": float(len(segment_df) / len(df) * 100) if len(df) > 0 else 0,
                "agent_ids": [int(x) for x in segment_df['AGENT_ID'].tolist() if pd.notna(x)],
                "statistics": {},
                "insights": []
            }

            # Calculate segment-specific statistics
            segment_stats = {}

            # AUM statistics
            if 'AUM_SELFREPORTED' in segment_df.columns:
                aum_data = pd.to_numeric(segment_df['AUM_SELFREPORTED'], errors='coerce')
                segment_stats['aum'] = {
                    "mean": float(aum_data.mean()) if not aum_data.empty and pd.notna(aum_data.mean()) else 0,
                    "median": float(aum_data.median()) if not aum_data.empty and pd.notna(aum_data.median()) else 0,
                    "min": float(aum_data.min()) if not aum_data.empty and pd.notna(aum_data.min()) else 0,
                    "max": float(aum_data.max()) if not aum_data.empty and pd.notna(aum_data.max()) else 0
                }

            # NPS statistics
            if 'NPS_SCORE' in segment_df.columns:
                nps_data = pd.to_numeric(segment_df['NPS_SCORE'], errors='coerce')
                segment_stats['nps'] = {
                    "mean": float(nps_data.mean()) if not nps_data.empty and pd.notna(nps_data.mean()) else 0,
                    "median": float(nps_data.median()) if not nps_data.empty and pd.notna(nps_data.median()) else 0,
                    "promoters": int((nps_data >= 9).sum()),
                    "passives": int(((nps_data >= 7) & (nps_data <= 8)).sum()),
                    "detractors": int((nps_data <= 6).sum())
                }

            # Tenure statistics
            if 'AGENT_TENURE' in segment_df.columns:
                tenure_data = pd.to_numeric(segment_df['AGENT_TENURE'], errors='coerce')
                segment_stats['tenure'] = {
                    "mean": float(tenure_data.mean()) if not tenure_data.empty and pd.notna(tenure_data.mean()) else 0,
                    "median": float(tenure_data.median()) if not tenure_data.empty and pd.notna(tenure_data.median()) else 0,
                    "min": float(tenure_data.min()) if not tenure_data.empty and pd.notna(tenure_data.min()) else 0,
                    "max": float(tenure_data.max()) if not tenure_data.empty and pd.notna(tenure_data.max()) else 0
                }

            # Sales performance
            if 'NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS' in segment_df.columns:
                sales_data = pd.to_numeric(segment_df['NO_OF_UNIQUE_POLICIES_SOLD_LAST_12_MONTHS'], errors='coerce')
                segment_stats['sales_performance'] = {
                    "mean": float(sales_data.mean()) if not sales_data.empty and pd.notna(sales_data.mean()) else 0,
                    "total_policies": int(sales_data.sum()) if not sales_data.empty and pd.notna(sales_data.sum()) else 0
                }

            # Purchase habits analysis
            purchase_habit_columns = [
                'PURCHASE_HABITS_APPAREL',
                'PURCHASE_HABITS_COMPUTERS',
                'PURCHASE_HABITS_FITNESS',
                'PURCHASE_HABITS_TRAVEL',
                'PURCHASE_HABITS_OTHERS'
            ]

            purchase_habits = {}
            for col in purchase_habit_columns:
                if col in segment_df.columns:
                    habit_data = pd.to_numeric(segment_df[col], errors='coerce')
                    habit_name = col.replace('PURCHASE_HABITS_', '').lower()
                    purchase_habits[habit_name] = {
                        "mean": float(habit_data.mean()) if not habit_data.empty and pd.notna(habit_data.mean()) else 0,
                        "count": int((habit_data > 0).sum()) if not habit_data.empty else 0
                    }

            # Identify top purchase habits for this segment
            if purchase_habits:
                segment_stats['purchase_habits'] = purchase_habits
                # Find top 2 habits by mean value
                sorted_habits = sorted(purchase_habits.items(), key=lambda x: x[1]['mean'], reverse=True)
                segment_stats['top_purchase_habits'] = [habit[0] for habit in sorted_habits[:2] if habit[1]['mean'] > 0]

            segment_breakdown['statistics'] = segment_stats

            # Generate segment-specific insights
            insights = []
            insights.append(f"{segment_name}: {len(segment_df)} agents ({segment_breakdown['percentage_of_total']:.1f}% of filtered population)")

            if segment_stats.get('aum'):
                avg_aum = segment_stats['aum']['mean']
                insights.append(f"Average AUM: ${avg_aum:,.0f}")

            if segment_stats.get('nps'):
                avg_nps = segment_stats['nps']['mean']
                insights.append(f"Average NPS: {avg_nps:.1f}")

            if segment_stats.get('tenure'):
                avg_tenure = segment_stats['tenure']['mean']
                insights.append(f"Average tenure: {avg_tenure:.1f} years")

            segment_breakdown['insights'] = insights

            segments_breakdown[segment_name] = segment_breakdown

        return segments_breakdown
