"""Campaign Strategist Agent - Recommends campaign approach and strategy."""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.agents.base_agent import BaseAgent, Message
from src.core.config import get_settings
from src.llm import ClaudeProvider


class CampaignStrategistAgent(BaseAgent):
    """
    Campaign Strategist Agent that recommends campaign approach and strategy.
    
    Responsibilities:
    1. Analyze segment profile and original goal
    2. Suggest messaging strategies
    3. Recommend optimal channels for outreach
    4. Provide timing recommendations
    5. Return comprehensive campaign strategy
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize campaign strategist agent.
        
        Args:
            config: Agent configuration from config.yaml
        """
        settings = get_settings()
        agent_config = settings.get_agent_config('campaign_strategist')
        super().__init__("CampaignStrategistAgent", agent_config)
        
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
        Generate comprehensive campaign strategy.
        
        Args:
            message: Message containing profile analysis and original goal
            
        Returns:
            Dictionary with campaign strategy recommendations
        """
        try:
            # Extract profile analysis and original goal
            profiles = message.content.get('profiles', {})
            goal = message.content.get('goal', '')
            criteria = message.content.get('criteria', {})
            
            if not profiles.get('success'):
                raise ValueError("No valid profile analysis provided")
            
            # Extract key information
            segment_summary = profiles.get('segment_summary', {})
            statistics = profiles.get('statistics', {})
            insights = profiles.get('insights', {})
            segment_description = profiles.get('segment_description', '')
            agent_profiles = profiles.get('agent_profiles', [])
            segments_breakdown = profiles.get('segments_breakdown', {})

            # Check if we have segment breakdown for per-segment strategies
            if segments_breakdown:
                # Generate strategy per segment
                return self._generate_per_segment_strategies(
                    goal, criteria, segment_summary, segments_breakdown
                )
            else:
                # Fallback: Generate single unified strategy (original behavior)
                return self._generate_unified_strategy(
                    goal, criteria, segment_summary, statistics, insights,
                    segment_description, agent_profiles
                )
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Campaign strategy generation failed: {str(e)}",
                "campaign_strategy": {},
                "confidence_score": 0.0
            }
    
    def _generate_messaging_strategy(self, goal: str, criteria: Dict[str, Any], 
                                  segment_summary: Dict[str, Any], 
                                  statistics: Dict[str, Any], 
                                  insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate messaging strategy based on segment characteristics.
        
        Args:
            goal: Original campaign goal
            criteria: Parsed criteria
            segment_summary: Segment summary
            statistics: Segment statistics
            insights: Generated insights
            
        Returns:
            Messaging strategy recommendations
        """
        objective = criteria.get('objective', 'unknown')
        
        # Base messaging themes by objective
        messaging_themes = {
            'retention': {
                "primary_message": "Value recognition and exclusive benefits",
                "emotional_hooks": ["appreciation", "exclusivity", "long-term partnership", "special recognition"],
                "key_benefits": ["VIP status", "premium services", "priority support", "exclusive products"],
                "tone": "appreciative, exclusive, professional"
            },
            'acquisition': {
                "primary_message": "Growth opportunity and competitive advantage",
                "emotional_hooks": ["success", "growth", "excellence", "achievement"],
                "key_benefits": ["superior products", "better support", "industry leadership", "proven results"],
                "tone": "motivational, confident, professional"
            },
            'upsell': {
                "primary_message": "Enhanced protection and premium solutions",
                "emotional_hooks": ["security", "protection", "peace_of_mind", "comprehensive_coverage"],
                "key_benefits": ["complete protection", "premium features", "expert support", "value-added services"],
                "tone": "consultative, informative, reassuring"
            },
            'winback': {
                "primary_message": "Improved service and renewed commitment",
                "emotional_hooks": ["second_chance", "improvement", "renewal", "fresh_start"],
                "key_benefits": ["enhanced service", "new features", "better support", "special offers"],
                "tone": "apologetic, optimistic, committed"
            }
        }
        
        theme = messaging_themes.get(objective, messaging_themes['retention'])
        
        # Customize based on segment characteristics
        avg_aum = statistics.get('aum', {}).get('mean', 0)
        avg_nps = statistics.get('nps', {}).get('mean', 0)
        
        if avg_aum > 5000000:
            theme['customization'] = "Premium messaging: Focus on sophisticated products and exclusive services"
        elif avg_aum > 2000000:
            theme['customization'] = "Value messaging: Emphasize quality products and excellent support"
        else:
            theme['customization'] = "Accessibility messaging: Highlight affordability and great value"
        
        if avg_nps >= 8:
            theme['special_focus'] = "Leverage satisfaction: Highlight their positive experience and seek advocacy"
        elif avg_nps <= 6:
            theme['special_focus'] = "Address concerns: Acknowledge past issues and demonstrate improvement"
        
        return {
            "primary_message": theme['primary_message'],
            "emotional_hooks": theme['emotional_hooks'],
            "key_benefits": theme['key_benefits'],
            "tone": theme['tone'],
            "customization": theme.get('customization', ''),
            "special_focus": theme.get('special_focus', ''),
            "sample_headlines": self._generate_sample_headlines(theme, objective),
            "call_to_action": self._generate_call_to_action(objective)
        }
    
    def _recommend_channels(self, statistics: Dict[str, Any], 
                          insights: Dict[str, Any], 
                          agent_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommend optimal channels for campaign outreach.
        
        Args:
            statistics: Segment statistics
            insights: Generated insights
            agent_profiles: Individual agent profiles
            
        Returns:
            Channel recommendations
        """
        channels = {
            "digital": {
                "email": {"priority": "high", "reasoning": "Direct, personalized communication"},
                "website_portal": {"priority": "medium", "reasoning": "Self-service convenience"},
                "mobile_app": {"priority": "medium", "reasoning": "On-the-go access"}
            },
            "traditional": {
                "phone": {"priority": "high", "reasoning": "Personal relationship building"},
                "direct_mail": {"priority": "medium", "reasoning": "Tangible, memorable"},
                "fax": {"priority": "low", "reasoning": "Legacy preference"}
            },
            "events": {
                "webinars": {"priority": "medium", "reasoning": "Educational engagement"},
                "conferences": {"priority": "medium", "reasoning": "Networking opportunities"},
                "training": {"priority": "high", "reasoning": "Professional development"}
            }
        }
        
        # Customize based on segment characteristics
        avg_age = statistics.get('demographics', {}).get('age', {}).get('mean', 45)
        avg_tenure = statistics.get('tenure', {}).get('mean', 5)
        
        # Digital preferences based on age
        if avg_age < 40:
            channels['digital']['email']['priority'] = 'high'
            channels['digital']['mobile_app']['priority'] = 'high'
            channels['traditional']['fax']['priority'] = 'low'
        elif avg_age > 60:
            channels['traditional']['phone']['priority'] = 'high'
            channels['traditional']['direct_mail']['priority'] = 'high'
            channels['digital']['mobile_app']['priority'] = 'low'
        
        # Channel preferences based on tenure
        if avg_tenure > 10:
            channels['traditional']['phone']['priority'] = 'high'
            channels['events']['conferences']['priority'] = 'high'
        elif avg_tenure < 2:
            channels['events']['training'].update({"priority": "high", "reasoning": "Onboarding and skill development"})
        
        return {
            "recommended_channels": channels,
            "primary_channel": self._determine_primary_channel(channels),
            "channel_sequence": self._generate_channel_sequence(channels),
            "personalization_tips": self._generate_personalization_tips(insights)
        }
    
    def _generate_timing_strategy(self, criteria: Dict[str, Any], 
                               statistics: Dict[str, Any], 
                               agent_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate timing strategy for campaign execution.
        
        Args:
            criteria: Campaign criteria
            statistics: Segment statistics
            agent_profiles: Agent profiles
            
        Returns:
            Timing strategy recommendations
        """
        # Base timing
        campaign_duration = "4-6 weeks"
        
        # Optimal days/times based on agent characteristics
        avg_age = statistics.get('demographics', {}).get('age', {}).get('mean', 45)
        
        if avg_age < 40:
            best_days = ["Tuesday", "Wednesday", "Thursday"]
            best_times = ["9:00 AM - 11:00 AM", "2:00 PM - 4:00 PM"]
        elif avg_age >= 60:
            best_days = ["Tuesday", "Wednesday"]
            best_times = ["10:00 AM - 12:00 PM", "1:00 PM - 3:00 PM"]
        else:
            best_days = ["Tuesday", "Wednesday", "Thursday"]
            best_times = ["9:00 AM - 11:00 AM", "1:00 PM - 3:00 PM"]
        
        # Month preferences (avoid holiday seasons for new agents)
        avg_tenure = statistics.get('tenure', {}).get('mean', 5)
        if avg_tenure < 2:
            best_months = ["January", "February", "September", "October"]
            avoid_months = ["November", "December", "June", "July"]
        else:
            best_months = ["January", "February", "March", "October", "November"]
            avoid_months = ["August", "December"]
        
        return {
            "campaign_timeline": {
                "duration": campaign_duration,
                "phases": [
                    {"phase": "Awareness", "duration": "1-2 weeks", "goal": "Generate interest"},
                    {"phase": "Consideration", "duration": "2-3 weeks", "goal": "Build engagement"},
                    {"phase": "Decision", "duration": "1 week", "goal": "Drive action"}
                ]
            },
            "optimal_timing": {
                "best_days": best_days,
                "best_times": best_times,
                "avoid_times": ["Early morning", "Late evening", "Lunch hours"]
            },
            "seasonal_recommendations": {
                "best_months": best_months,
                "avoid_months": avoid_months,
                "reasoning": "Based on agent tenure and business cycle"
            },
            "follow_up_schedule": [
                {"timing": "Immediate", "type": "Confirmation"},
                {"timing": "1 day", "type": "Engagement"},
                {"timing": "1 week", "type": "Value offer"},
                {"timing": "2 weeks", "type": "Push messaging"},
                {"timing": "1 month", "type": "Relationship building"}
            ]
        }
    
    def _generate_budget_recommendations(self, segment_summary: Dict[str, Any], 
                                       statistics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate budget recommendations based on segment value.
        
        Args:
            segment_summary: Segment summary
            statistics: Segment statistics
            
        Returns:
            Budget recommendations
        """
        total_agents = segment_summary.get('total_agents', 0)
        avg_aum = statistics.get('aum', {}).get('mean', 0)
        
        # Base budget per agent
        if avg_aum > 5000000:
            budget_per_agent = 500  # High-value segment
            budget_rationale = "Premium budget justified by high AUM potential"
        elif avg_aum > 2000000:
            budget_per_agent = 250  # Mid-value segment
            budget_rationale = "Standard budget for moderate-value agents"
        else:
            budget_per_agent = 150  # Standard segment
            budget_rationale = "Cost-effective budget for standard-value agents"
        
        total_budget = total_agents * budget_per_agent
        
        # Budget allocation
        allocation = {
            "creative_development": {"percentage": 20, "amount": total_budget * 0.2},
            "channel_execution": {"percentage": 60, "amount": total_budget * 0.6},
            "measurement_tracking": {"percentage": 10, "amount": total_budget * 0.1},
            "optimization": {"percentage": 10, "amount": total_budget * 0.1}
        }
        
        return {
            "total_budget": total_budget,
            "budget_per_agent": budget_per_agent,
            "rationale": budget_rationale,
            "allocation": allocation,
            "roi_expectations": self._calculate_roi_expectations(total_budget, avg_aum),
            "budget_optimization_tips": [
                "Focus 70% budget on highest-performing channels",
                "Use A/B testing to optimize message performance",
                "Implement automated follow-up to reduce manual costs"
            ]
        }
    
    def _define_success_metrics(self, criteria: Dict[str, Any], 
                              segment_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define success metrics for the campaign.
        
        Args:
            criteria: Campaign criteria
            segment_summary: Segment summary
            
        Returns:
            Success metrics definition
        """
        objective = criteria.get('objective', 'unknown')
        total_agents = segment_summary.get('total_agents', 0)
        
        # Base metrics by objective
        metrics_library = {
            'retention': {
                "primary_kpi": "Retention Rate",
                "target_rate": "90%+",
                "secondary_kpis": [
                    "Renewal Rate: 85%+",
                    "Satisfaction Score: 8.5+",
                    "Advocacy Score: 40%+"
                ],
                "engagement_metrics": [
                    "Email Open Rate: 25%+",
                    "Phone Answer Rate: 60%+",
                    "Portal Login Increase: 30%+"
                ]
            },
            'acquisition': {
                "primary_kpi": "Conversion Rate",
                "target_rate": "15%+",
                "secondary_kpis": [
                    "New Business Growth: 20%+",
                    "Pipeline Creation: 50+ opportunities",
                    "Sales Cycle Reduction: 15%+"
                ],
                "engagement_metrics": [
                    "Email Response Rate: 10%+",
                    "Meeting Requests: 25%+",
                    "Website Traffic: 40%+"
                ]
            },
            'upsell': {
                "primary_kpi": "Upsell Rate",
                "target_rate": "25%+",
                "secondary_kpis": [
                    "Revenue Increase per Agent: $50K+",
                    "Product Adoption: 30%+",
                    "Cross-sell Rate: 20%+"
                ],
                "engagement_metrics": [
                    "Product Interest: 35%+",
                    "Consultation Requests: 20%+",
                    "Proposal Acceptance: 60%+"
                ]
            }
        }
        
        metrics = metrics_library.get(objective, metrics_library['retention'])
        
        return {
            "objective": objective,
            "primary_kpi": metrics['primary_kpi'],
            "target_rate": metrics['target_rate'],
            "secondary_kpis": metrics['secondary_kpis'],
            "engagement_metrics": metrics['engagement_metrics'],
            "measurement_timeline": "30, 60, 90 days",
            "reporting_frequency": "Weekly during campaign, Monthly post-campaign",
            "baseline_metrics": self._get_baseline_metrics(total_agents)
        }
    
    def _generate_overall_strategy(self, goal: str, segment_summary: Dict[str, Any], 
                                 insights: Dict[str, Any], messaging_strategy: Dict[str, Any],
                                 channel_recommendations: Dict[str, Any], 
                                 timing_strategy: Dict[str, Any]) -> str:
        """
        Generate comprehensive overall campaign strategy using LLM.
        
        Returns:
            LLM-generated overall strategy
        """
        strategy_context = {
            "objective": segment_summary.get('objective', 'unknown'),
            "segment_size": segment_summary.get('total_agents', 0),
            "key_insights": insights.get('key_findings', []),
            "messaging_theme": messaging_strategy.get('primary_message', ''),
            "primary_channel": channel_recommendations.get('primary_channel', 'email'),
            "timeline": timing_strategy.get('campaign_timeline', {}).get('duration', '4-6 weeks')
        }
        
        prompt = f"""
        Create a comprehensive campaign strategy for this insurance agent campaign:
        
        CAMPAIGN CONTEXT:
        - Original Goal: "{goal}"
        - Objective: {strategy_context['objective']}
        - Target Segment: {strategy_context['segment_size']} agents
        - Timeline: {strategy_context['timeline']}
        
        KEY INSIGHTS:
        {strategy_context['key_insights']}
        
        MESSAGING APPROACH:
        {strategy_context['messaging_theme']}
        
        PRIMARY CHANNEL:
        {strategy_context['primary_channel']}
        
        Please provide a comprehensive 4-paragraph campaign strategy that includes:
        1. Strategic Overview and Objectives
        2. Target Audience Analysis and Approach
        3. Implementation Framework and Tactics
        4. Expected Outcomes and Success Factors
        
        Focus on actionable insights and measurable results.
        """
        
        try:
            strategy = self.llm.query(
                prompt=prompt,
                system="You are a senior insurance marketing strategist with expertise in agent relationship management and campaign optimization."
            )
            return strategy
        except Exception as e:
            return f"Strategic campaign approach focusing on {strategy_context['objective']} for {strategy_context['segment_size']} high-value agents using {strategy_context['messaging_theme']} messaging delivered via {strategy_context['primary_channel']} over {strategy_context['timeline']} period."
    
    def _generate_implementation_plan(self, messaging_strategy: Dict[str, Any], 
                                    channel_recommendations: Dict[str, Any], 
                                    timing_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate step-by-step implementation plan.
        
        Returns:
            Implementation plan steps
        """
        return [
            {
                "week": 1,
                "phase": "Setup & Launch",
                "activities": [
                    "Finalize messaging and creative assets",
                    "Set up campaign tracking and analytics",
                    "Segment agent lists by channel preference",
                    "Launch initial awareness phase"
                ]
            },
            {
                "week": 2,
                "phase": "Awareness Building",
                "activities": [
                    "Deploy multi-channel awareness campaigns",
                    "Monitor engagement metrics",
                    "Begin personalized outreach",
                    "Gather initial feedback"
                ]
            },
            {
                "week": 3-4,
                "phase": "Engagement & Conversion",
                "activities": [
                    "Intensify personalized messaging",
                    "Conduct direct sales activities",
                    "Provide additional value-added content",
                    "Track conversion metrics"
                ]
            },
            {
                "week": 5-6,
                "phase": "Follow-up & Optimization",
                "activities": [
                    "Follow up with non-responders",
                    "Optimize messaging based on results",
                    "Conduct final push activities",
                    "Begin relationship nurturing"
                ]
            }
        ]
    
    def _calculate_confidence_score(self, segment_summary: Dict[str, Any], 
                                 statistics: Dict[str, Any], 
                                 insights: Dict[str, Any]) -> float:
        """
        Calculate confidence score for campaign success.
        
        Returns:
            Confidence score (0.0 - 1.0)
        """
        score = 0.5  # Base score
        
        # Higher scores for larger segments
        total_agents = segment_summary.get('total_agents', 0)
        if total_agents > 10:
            score += 0.2
        elif total_agents > 5:
            score += 0.1
        
        # Higher scores for better NPS
        avg_nps = statistics.get('nps', {}).get('mean', 0)
        if avg_nps >= 8:
            score += 0.2
        elif avg_nps >= 6:
            score += 0.1
        
        # Higher scores for higher AUM
        avg_aum = statistics.get('aum', {}).get('mean', 0)
        if avg_aum > 3000000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_sample_headlines(self, theme: Dict[str, Any], objective: str) -> List[str]:
        """Generate sample headlines for the campaign."""
        headlines = {
            'retention': [
                "You're Part of Our Elite Agent Network - Exclusive Opportunities Await",
                "VIP Recognition: Unlock Premium Benefits Reserved for Top Performers",
                "Your Success Story Continues - Special Offers Just for You"
            ],
            'acquisition': [
                "Join the Leaders: Exclusive Opportunities for Top Insurance Agents",
                "Elevate Your Business: Premium Products for High-Achieving Agents",
                "Where Excellence Meets Opportunity - Your Path to Greater Success"
            ],
            'upsell': [
                "Protect What Matters Most: Enhanced Coverage for Your Valued Clients",
                "Complete Protection Starts Here - Premium Solutions Tailored for You",
                "Upgrade Your Portfolio: Advanced Products for Serious Professionals"
            ]
        }
        return headlines.get(objective, headlines['retention'])
    
    def _generate_call_to_action(self, objective: str) -> str:
        """Generate appropriate call-to-action based on objective."""
        ctas = {
            'retention': "Schedule your exclusive consultation today",
            'acquisition': "Discover how we can accelerate your success",
            'upsell': "Enhance your protection portfolio now",
            'winback': "Let's restart our partnership stronger than ever"
        }
        return ctas.get(objective, "Learn more about our premium services")
    
    def _determine_primary_channel(self, channels: Dict[str, Any]) -> str:
        """Determine the primary channel from recommendations."""
        high_priority_channels = []
        for category, channel_list in channels.items():
            for channel, config in channel_list.items():
                if config.get('priority') == 'high':
                    high_priority_channels.append(channel)
        
        return high_priority_channels[0] if high_priority_channels else 'email'
    
    def _generate_channel_sequence(self, channels: Dict[str, Any]) -> List[str]:
        """Generate optimal channel sequence."""
        return ['email', 'phone', 'website_portal', 'direct_mail']
    
    def _generate_personalization_tips(self, insights: Dict[str, Any]) -> List[str]:
        """Generate personalization tips based on insights."""
        tips = ["Use agent's actual AUM amount in messages"]
        key_findings = insights.get('key_findings', [])
        
        if any('satisfaction' in finding.lower() for finding in key_findings):
            tips.append("Reference their positive NPS experience")
        
        if any('tenure' in finding.lower() for finding in key_findings):
            tips.append("Acknowledge their years of experience")
        
        return tips
    
    def _calculate_roi_expectations(self, budget: float, avg_aum: float) -> Dict[str, Any]:
        """Calculate ROI expectations."""
        if avg_aum > 5000000:
            expected_revenue = budget * 3
            roi_percentage = 200
        elif avg_aum > 2000000:
            expected_revenue = budget * 2.5
            roi_percentage = 150
        else:
            expected_revenue = budget * 2
            roi_percentage = 100
        
        return {
            "expected_revenue": expected_revenue,
            "roi_percentage": roi_percentage,
            "payback_period": "90-120 days"
        }
    
    def _get_baseline_metrics(self, total_agents: int) -> Dict[str, Any]:
        """Get baseline metrics for comparison."""
        return {
            "current_engagement_rate": "12%",  # Industry average
            "average_response_time": "2-3 days",
            "satisfaction_baseline": "75%",
            "monthly_interaction_frequency": "2-3 times"
        }

    def _generate_per_segment_strategies(
        self,
        goal: str,
        criteria: Dict[str, Any],
        segment_summary: Dict[str, Any],
        segments_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate separate campaign strategy for each customer segment.

        Args:
            goal: Campaign goal
            criteria: Parsed criteria
            segment_summary: Overall segment summary
            segments_breakdown: Per-segment breakdowns from ProfileGenerator

        Returns:
            Campaign strategies per segment
        """
        segment_strategies = {}

        for segment_name, segment_data in segments_breakdown.items():
            # Generate strategy for this segment
            strategy = self._generate_single_segment_strategy(
                segment_name, segment_data, goal, criteria
            )
            segment_strategies[segment_name] = strategy

        return {
            "success": True,
            "objective": criteria.get('objective', 'unknown'),
            "total_agents": segment_summary.get('total_agents', 0),
            "segment_strategies": segment_strategies,
            "confidence_score": self._calculate_overall_confidence(segments_breakdown)
        }

    def _generate_single_segment_strategy(
        self,
        segment_name: str,
        segment_data: Dict[str, Any],
        goal: str,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate campaign strategy for a single customer segment.

        Args:
            segment_name: Name of the segment
            segment_data: Segment-specific data and statistics
            goal: Campaign goal
            criteria: Parsed criteria
            overall_summary: Overall campaign summary

        Returns:
            Strategy for this segment
        """
        stats = segment_data['statistics']
        insights = segment_data['insights']
        agent_count = segment_data['agent_count']

        # Generate strategy components for this segment
        messaging = self._generate_segment_messaging(segment_name, stats, criteria)
        channels = self._generate_segment_channels(segment_name, stats)
        budget = self._generate_segment_budget(agent_count, stats)

        # Generate LLM-powered strategy for this segment
        segment_strategy = self._generate_segment_llm_strategy(
            segment_name, segment_data, goal, criteria
        )

        return {
            "segment_name": segment_name,
            "agent_count": agent_count,
            "percentage_of_campaign": segment_data['percentage_of_total'],
            "strategy_narrative": segment_strategy,
            "messaging": messaging,
            "channels": channels,
            "budget": budget,
            "key_insights": insights
        }

    def _generate_segment_llm_strategy(
        self,
        segment_name: str,
        segment_data: Dict[str, Any],
        goal: str,
        criteria: Dict[str, Any]
    ) -> str:
        """
        Generate LLM-powered strategy narrative for a specific segment.

        Args:
            segment_name: Customer segment name
            segment_data: Segment statistics and insights
            goal: Campaign goal
            criteria: Campaign criteria

        Returns:
            Strategy narrative string
        """
        stats = segment_data['statistics']
        insights = segment_data['insights']
        agent_count = segment_data['agent_count']

        # Build segment characteristics description
        segment_characteristics = {
            "Independent Agents": "value autonomy, flexibility, and self-directed business models",
            "Emerging Experts": "are building expertise, seek growth opportunities and professional development",
            "Accomplished Professionals": "have established practices, value sophisticated solutions and recognition",
            "Comfortable Retirees": "prioritize stability, long-term relationships, and legacy preservation"
        }

        characteristics = segment_characteristics.get(segment_name, "have unique needs and preferences")

        # Extract purchase habits for personalization
        top_habits = stats.get('top_purchase_habits', [])
        purchase_habits_detail = stats.get('purchase_habits', {})

        # Pick dominant habit (highest scoring)
        dominant_habit = top_habits[0] if top_habits else None

        # Build habits summary
        habits_text = f"Dominant interest: {dominant_habit}" if dominant_habit else "No strong purchase habits"

        # Create tagline based on dominant habit
        habit_taglines = {
            'fitness': 'Fitness Enthusiasts',
            'travel': 'Travel Seekers',
            'computers': 'Tech Savvy',
            'apparel': 'Style Conscious',
            'others': 'Diverse Interests'
        }
        segment_tagline = habit_taglines.get(dominant_habit, 'Balanced Profile')

        # Determine sales milestone based on tenure and current performance
        avg_tenure = stats.get('tenure', {}).get('mean', 0)
        avg_policies = stats.get('sales_performance', {}).get('mean', 0)

        prompt = f"""
        Brief campaign strategy for "{segment_name}" ({segment_tagline}).

        DATA: {agent_count} agents | AUM: ${stats.get('aum', {}).get('mean', 0):,.0f} | NPS: {stats.get('nps', {}).get('mean', 0):.1f} | Tenure: {avg_tenure:.1f}y | Sales: {avg_policies:.1f}
        INTEREST: {habits_text}
        GOAL: {criteria.get('objective', 'unknown')}

        **Profile Summary**
        [1 sentence mentioning their {dominant_habit if dominant_habit else 'interest'} preference + key challenge/opportunity]

        **Engagement Tactics**

        1. Performance Incentive: [Milestone] → [Reward $100-200]
           Milestones: New agents (<2y): "2 policies in 60 days" | Mid (2-5y): "5 policies in Q4" | Vets (5+y): "$500K AUM"
           Rewards by interest:
           - fitness: $150 gym membership, fitness tracker + gear, sports tickets
           - travel: $200 travel voucher, premium luggage, hotel gift card
           - computers: Wireless headphones, smart watch, tech accessories bundle
           - apparel: $150 clothing allowance, designer accessories
           - none: $150 gift card, cash bonus

        2. Training: [Pick one based on tenure {avg_tenure:.1f}y]
           New: Sales fundamentals, 1-1 coaching | Mid: Product certification, leadership workshop | Vet: Executive masterclass

        3. Recognition: [Pick one based on segment]
           New: New agent spotlight | Mid: Regional leaderboard, peer network | Vet: Advisory board invite, achievement award

        Keep it concise. One line per tactic.
        """

        try:
            strategy = self.llm.query(
                prompt=prompt,
                system="You are an expert insurance marketing strategist specializing in agent segmentation and personalized campaign strategies."
            )
            return strategy
        except Exception as e:
            return f"Strategy for {segment_name}: {agent_count} agents with avg AUM ${stats.get('aum', {}).get('mean', 0):,.0f}. Focus on segment-specific needs and {criteria.get('objective', 'engagement')}."

    def _generate_segment_messaging(self, segment_name: str, stats: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Generate messaging strategy for specific segment."""
        objective = criteria.get('objective', 'retention')

        # Segment-specific messaging themes
        messaging_by_segment = {
            "Independent Agents": {
                "tone": "empowering, flexible, results-oriented",
                "key_message": "Your independence, our support",
                "hooks": ["autonomy", "flexibility", "partnership", "results"]
            },
            "Emerging Experts": {
                "tone": "motivational, educational, growth-focused",
                "key_message": "Accelerate your path to excellence",
                "hooks": ["growth", "learning", "mentorship", "advancement"]
            },
            "Accomplished Professionals": {
                "tone": "sophisticated, exclusive, prestigious",
                "key_message": "Recognition for your achievements",
                "hooks": ["prestige", "sophistication", "legacy", "excellence"]
            },
            "Comfortable Retirees": {
                "tone": "reassuring, stable, appreciative",
                "key_message": "Honoring your legacy, securing your future",
                "hooks": ["stability", "legacy", "appreciation", "security"]
            }
        }

        return messaging_by_segment.get(segment_name, {
            "tone": "professional, respectful",
            "key_message": "Partnering for success",
            "hooks": ["partnership", "trust", "value"]
        })

    def _generate_segment_channels(self, segment_name: str, stats: Dict[str, Any]) -> List[str]:
        """Recommend channels for specific segment."""
        # Segment-specific channel preferences
        channels_by_segment = {
            "Independent Agents": ["email", "mobile_app", "self-service_portal"],
            "Emerging Experts": ["webinars", "training", "email", "social_media"],
            "Accomplished Professionals": ["phone", "executive_events", "email", "direct_mail"],
            "Comfortable Retirees": ["phone", "direct_mail", "in_person_meetings"]
        }

        return channels_by_segment.get(segment_name, ["email", "phone"])

    def _generate_segment_budget(self, agent_count: int, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate budget for specific segment."""
        avg_aum = stats.get('aum', {}).get('mean', 0)

        # Budget per agent based on AUM
        if avg_aum > 5000000:
            budget_per_agent = 120
        elif avg_aum > 2000000:
            budget_per_agent = 100
        else:
            budget_per_agent = 80

        total_budget = agent_count * budget_per_agent

        return {
            "total_budget": total_budget,
            "budget_per_agent": budget_per_agent,
            "rationale": f"Budget based on segment AUM (${avg_aum:,.0f} avg)"
        }

    def _calculate_overall_confidence(self, segments_breakdown: Dict[str, Any]) -> float:
        """Calculate overall confidence score across all segments."""
        if not segments_breakdown:
            return 0.5

        # Higher confidence for larger, more balanced segments
        segment_counts = [data['agent_count'] for data in segments_breakdown.values()]
        total_agents = sum(segment_counts)

        if total_agents > 10:
            return 0.8
        elif total_agents > 5:
            return 0.7
        else:
            return 0.6

    def _generate_unified_strategy(
        self,
        goal: str,
        criteria: Dict[str, Any],
        segment_summary: Dict[str, Any],
        statistics: Dict[str, Any],
        insights: Dict[str, Any],
        segment_description: str,
        agent_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate single unified strategy (original behavior - fallback when no segment breakdown).
        """
        # Generate campaign strategy components (original logic)
        messaging_strategy = self._generate_messaging_strategy(
            goal, criteria, segment_summary, statistics, insights
        )

        channel_recommendations = self._recommend_channels(
            statistics, insights, agent_profiles
        )

        timing_strategy = self._generate_timing_strategy(
            criteria, statistics, agent_profiles
        )

        budget_recommendations = self._generate_budget_recommendations(
            segment_summary, statistics
        )

        success_metrics = self._define_success_metrics(
            criteria, segment_summary
        )

        # Generate comprehensive strategy using LLM
        overall_strategy = self._generate_overall_strategy(
            goal, segment_summary, insights, messaging_strategy,
            channel_recommendations, timing_strategy
        )

        return {
            "success": True,
            "campaign_strategy": {
                "objective": criteria.get('objective', 'unknown'),
                "target_segment": segment_summary,
                "expected_reach": segment_summary.get('total_agents', 0),
                "overall_strategy": overall_strategy,
                "messaging": messaging_strategy,
                "channels": channel_recommendations,
                "timing": timing_strategy,
                "budget": budget_recommendations,
                "success_metrics": success_metrics,
                "implementation_plan": self._generate_implementation_plan(
                    messaging_strategy, channel_recommendations, timing_strategy
                )
            },
            "confidence_score": self._calculate_confidence_score(
                segment_summary, statistics, insights
            )
        }
