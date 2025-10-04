"""Campaign management endpoints."""

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.services import CampaignService

router = APIRouter()
campaign_service = CampaignService()


class Campaign(BaseModel):
    """Response model for campaign details."""
    campaign_id: str
    name: str
    goal: str
    target_criteria: Dict[str, Any]
    segment_size: int
    created_at: str
    status: str


class CampaignRequest(BaseModel):
    """Request model for campaign creation."""
    goal: str = Field(
        ...,
        description="Natural language campaign goal",
        example="Find high-value agents with excellent satisfaction for VIP retention"
    )
    campaign_name: Optional[str] = Field(
        None,
        description="Optional custom campaign name. If not provided, a name will be generated based on the goal.",
        example="Q4 High-Value Retention Campaign"
    )


class TodoItem(BaseModel):
    """Todo item in the execution plan."""
    step: int
    description: str
    agent: str
    active_form: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class CampaignResponse(BaseModel):
    """Response model for campaign creation."""
    success: bool
    campaign_id: str
    goal: str
    campaign_name: str
    created_at: str
    plan: List[TodoItem]
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/all", response_model=List[Campaign])
async def get_all_campaigns() -> List[Campaign]:
    """
    Get all existing campaigns.

    Returns:
        List of all campaigns with their details

    Example Response:
    ```json
    [
        {
            "campaign_id": "CAM001",
            "name": "Q4 High-Value Focus",
            "goal": "Target high-NPS agents with declining sales for Q4 boost",
            "target_criteria": {
                "nps_score": "high",
                "sales_trend": "declining"
            },
            "segment_size": 150,
            "created_at": "2025-09-15T10:30:00Z",
            "status": "completed"
        }
    ]
    ```
    """
    try:
        campaigns_data = campaign_service.get_all_campaigns()
        
        # Handle case where no campaigns exist
        if not campaigns_data:
            return []
        
        # Convert dictionaries to Pydantic models
        campaigns = []
        for campaign_dict in campaigns_data:
            try:
                # Ensure proper type conversion for numeric fields
                if 'segment_size' in campaign_dict:
                    campaign_dict['segment_size'] = int(campaign_dict['segment_size'])
                
                # Ensure target_criteria is a dict (should already be parsed by service)
                if isinstance(campaign_dict.get('target_criteria'), str):
                    import json
                    campaign_dict['target_criteria'] = json.loads(campaign_dict['target_criteria'])
                
                campaign = Campaign(**campaign_dict)
                campaigns.append(campaign)
            except Exception as validation_error:
                # Log the validation error but continue with other campaigns
                print(f"Warning: Skipping invalid campaign data: {validation_error}")
                print(f"Campaign data: {campaign_dict}")
                continue
        
        return campaigns
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving campaigns: {str(e)}"
        )

# dummy 
@router.post("/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest) -> CampaignResponse:
    """
    Create a new marketing campaign.

    Args:
        request: Campaign creation request with goal and optional campaign name

    Returns:
        Campaign creation result with execution plan and results
    """
    try:
        result = campaign_service.create_campaign(
            goal=request.goal,
            campaign_name=request.campaign_name
        )
        
        # Convert to CampaignResponse format
        return CampaignResponse(
            success=result.get('success', False),
            campaign_id=result.get('campaign_id', ''),
            goal=result.get('goal', request.goal),
            campaign_name=result.get('campaign_name', 'Unnamed Campaign'),
            created_at=result.get('created_at', ''),
            plan=result.get('plan', []),
            results=result.get('results'),
            error=result.get('error')
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating campaign: {str(e)}"
        )


# dummy 
@router.get("/{campaign_id}/plan")
async def get_campaign_plan(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the execution plan for a specific campaign.
    
    Args:
        campaign_id: The ID of the campaign
        
    Returns:
        Basic JSON response
    """
    return [{"step":1,"description":"Parse campaign goal and extract criteria","agent":"GoalParser","active_form":"Parsing campaign goal","status":"completed","started_at":"2025-10-04T23:06:57.686677","completed_at":"2025-10-04T23:07:00.103010","error":None},{"step":2,"description":"Load agent population data from CSV files","agent":"DataLoader","active_form":"Loading agent data","status":"completed","started_at":"2025-10-04T23:07:00.103016","completed_at":"2025-10-04T23:07:00.321975","error":None},{"step":3,"description":"Filter agents based on parsed criteria","agent":"SegmentationAgent","active_form":"Segmenting agent population","status":"completed","started_at":"2025-10-04T23:07:00.321984","completed_at":"2025-10-04T23:07:00.550158","error":None},{"step":4,"description":"Generate comprehensive agent profiles and insights","agent":"ProfileGeneratorAgent","active_form":"Analyzing segment characteristics","status":"completed","started_at":"2025-10-04T23:07:00.550165","completed_at":"2025-10-04T23:07:11.135598","error":None},{"step":5,"description":"Develop comprehensive campaign strategy and recommendations","agent":"CampaignStrategistAgent","active_form":"Creating campaign strategy","status":"completed","started_at":"2025-10-04T23:07:11.135608","completed_at":"2025-10-04T23:07:30.159769","error":None}]


@router.get("/{campaign_id}/result")
async def get_campaign_result(campaign_id: str = Path(..., description="Campaign ID")):
    """
    Get the results summary for a specific campaign.
    
    Args:
        campaign_id: The ID of the campaign
        
    Returns:
        Basic JSON response
    """
    return {"success":True,"campaign_strategy":{"objective":"retention","target_segment":{"total_agents":5,"agent_ids":[1669588675,2481317293,3489505915,3758535778,5773410055,5796093280,10873025907,11853099002,13059289542,16174913655,17401363528,18338171812,21397315618,27857851491,29332434154,31053268139,31869354470,36750214882,39267796900,44068873862,45300293787,46132624623,46837224630,49185746215,52861394506,57172355843,65651474295,66118446217,67444800032,70005450117,72084366341,72159598520,73447873384,74458880408,83827549253,86330396313,92537077182,95672860880,97010274061,98179305004,98321802075,98375050577,98477949204,98956407498,99746944208,100958329466,101157715900,101265215028,101375984747,104653207606,108087919448,109689726472,110323805251,111683581161,111685245041,113032182115,117048359656,120722818893,122838169796,124131167266,129480516572,129582464742,130439178404,132408534041,133245622596,133811070758,134399102442,139851388233,145300913374,145585704310,146032600162,146598052886,146647962748,148094659757,150990404443,153589389746,155661641183,156386907741,156917106125,157632524311,157875967574,159214330960,165203946043,165360632611,167758422575,170408744892,171292545699,173415182365,183011325755,184324140017,186029034416,190091226041,190744029296,191612100120,194342478197,197463664655,197498044681,197792672301,201142696419,202574314777,204817140118,204874096100,209681499411,211016136725,217507520878,218461881316,220227352697,220620531485,222808839530,224688690017,231326497049,234360672540,241265559432,242950862591,243019402300,243046909129,243649362368,249683009483,254282495555,255306210878,259374776437,264553574518,265329153170,266634887505,267781703411,267988896048,270583318839,276519623654,278552741557,279167225700,279666331707,282459870132,285352648110,285925402902,286115401543,288302037972,290141602708,290466914276,296568381759,298016219149,298415657143,299977421574,301816474979,307730475564,311518078224,313241877942,314753547645,316080991052,317687828847,319880511911,326684993434,332826515785,333311137161,339837013731,342553566249,343803580908,344254978748,345874797084,346560453616,347602355999,347762888321,352759677451,355879354537,358240672774,361222242010,361573768367,363498037755,375784874487,381820846095,388218071371,392253050043,394041127395,396995801872,400697355661,402742604213,403702421354,405595152738,406584566712,406994344128,410347560078,415938049902,418626644339,419853394899,421126912746,421153227289,421176851347,422389404670,424077310844,428773290525,429912044163,429976126814,430447375947,432231308322,434826078704,436830293212,437824968832,439540301416,440328013516,440416852674,440880268552,441027596989,443449280373,443723129024,443827052151,444025856197,444281067152,444630395638,444975994573,446122973844,446537287343,447408978465,447946554173,449488967001,451927450158,452772511752,454446596775,460267821284,460454755730,461149524073,461922658499,467082496925,467598877803,468157551543,468738388779,472115838812,477029772973,479940865536,481275168859,482247713254,482905078743,485007409954,488022410964,489044970828,491828500198,492229444840,494562813783,496494317001,497102270172,499013827700,501912047852,503646356375,504219448279,507762751187,509644535688,510255982063,510643306314,512895022946,514175096141,516038066442,518180809366,520073934489,520949108864,524126534485,524189036740,525309326818,526924717192,528664752778,531696277716,532114495532,532353658581,532377074498,532817191347,534939187399,536751321908,537000548100,537084045706,538011568422,538634449943,542239036737,544230563873,545291494029,545973093975,546000018625,546526326472,547918406126,548858783672,550396011279,551644154396,553249424496,559811830995,563083583942,563965220474,563982933094,565330327441,566010716759,566102927765,566181116369,566396809634,570840246650,573914264226,574210981694,574343580146,577215025133,577899345385,579589851991,581290127442,581508518278,582242485001,582725783899,583953548283,584656999388,584657545498,584896147069,588234011063,590624480263,591493748308,592268159438,594458968534,594473794739,598635147533,600948560509,602609584065,604560932059,605780193396,605965814705,610247699515,613281707668,613391674533,614297662105,616852890319,619575136147,620507093116,622107037749,624274608310,624827053016,627745482335,627997610765,628712890565,630418497311,631657751328,632722931858,632990944800,635115969922,635577360839,640468617130,641692990060,646986325952,648410204190,648734529524,650924933104,652410326905,656697597111,657102077742,657530245379,658658560166,661119735837,665208309226,665498161492,666748090261,670059513351,670749758077,671024803745,672266603839,673064172069,675031470934,678168765088,681057903985,681646036508,691002698982,692882845660,693226776400,693295815068,694028429882,694085248256,694574423851,696923190583,697673332699,700404804785,700998484132,703996963504,707019265584,708003864463,708914615221,709348733582,712144292218,713715333495,714163730044,715749038335,718398699218,718534619389,720585731839,722358686467,725681022993,726080252058,726822298190,727532036260,727715168740,727953296040,729129397507,729445695432,729696626744,730457735199,738117715391,738747377233,739723742083,741346966233,742007812626,742463410673,743715236078,743864814147,744494296387,746699049553,747660067391,747794556756,750179171024,751167190627,751261827414,752556487524,752852905517,754149576942,754656422303,755505867505,758424659722,762176322957,762588918089,762705636362,764699830300,764862478746,767897819278,769224214405,773630383948,776082631342,777148571250,777460557958,778122907194,782571465091,785812587782,785925143156,786528405976,788081495437,789040127847,791545841047,793484887812,795226503971,798450141347,809851967668,813206771125,813281868515,814336718230,816177518448,817529145280,818308768284,818545389019,819808349771,821788951692,823164372956,828666300824,829307153069,830072298837,830238433036,830339378738,832628698682,832756359940,833254696311,833886397985,834527988213,839467038947,839803544172,839882057924,841007820971,841243212480,842249607522,842329662390,847173731602,847379646794,847567611180,848990476466,849732604242,851492102398,854569407430,856433330355,856577534689,857263442887,857863880631,858336747969,858452904823,858818322243,859168612476,859869456915,860052423880,861032660041,864216230629,864415747133,865163646904,866168729360,867117377864,868985292647,869036342215,872046929280,873853842269,874931577402,874962576862,876663984829,878002019273,882207698334,886786761142,887152924576,889517996199,890252566430,890726045574,891002164215,891941959549,892703806677,893726180007,894863670452,896940124218,900558049791,901240486647,901336315052,901524081444,904571540667,905900644573,907008016604,907574189089,911751654350,913219413222,914317269272,914549680841,915847475987,916579471971,916812351116,918224570399,925340715725,925686850482,932432683741,933108305618,933316476203,934044778336,935845753428,940071000787,940217794721,944183397760,947082180328,949014793801,951896858356,952546473678,954831891749,955292401409,955393561263,956329089048,958233318524,958306229977,958735910636,959134973785,961118083696,961676099279,962127946426,962574712155,967550763617,967697828683,968153544782,971874522524,971983557902,972874896185,973002043843,976893318975,977996311435,981019556840,982334224944,983617542251,983942757753,984105912578,986653777325,990698573365,990911668180,991975320873,995804740176,995968347386,996834117149,998259367785,998767491293,999452634312],"objective":"retention","criteria_applied":[{"field":"AGENT_TENURE","operator":"<","value":1},{"field":"AUM_SELFREPORTED","operator":">","value":75}]},"expected_reach":5,"overall_strategy":"## High-Performer New Agent Retention Campaign Strategy\n\n**Strategic Overview and Objectives**\nThis campaign targets a critical retention opportunity by focusing on newly onboarded agents (within 12 months) who demonstrate exceptional performance relative to their peer cohort. The primary objective is to proactively retain these 5 high-value agents through strategic recognition and exclusive benefit positioning, preventing potential attrition during the vulnerable early tenure period. The campaign will leverage value recognition messaging to reinforce their exceptional status while providing tangible rewards that strengthen their commitment to the organization. By implementing this focused 4-6 week initiative, we aim to achieve a 100% retention rate within this segment while establishing a replicable framework for future high-performer recognition programs.\n\n**Target Audience Analysis and Approach**\nOur target segment represents newly acquired talent with proven performance capabilities, indicating strong potential for long-term value generation. These agents exhibit above-average premium production within their first year, suggesting effective sales acumen and market adaptation skills. However, as part of the \"moderate satisfaction segment,\" they present an improvement opportunity that requires immediate attention to prevent disengagement. The approach will emphasize their elite status within their cohort while addressing potential satisfaction gaps through personalized recognition and exclusive access to advanced resources. Given their newness to the organization, these agents likely value professional development opportunities, peer recognition, and clear advancement pathways more than tenured agents who may prioritize different benefits.\n\n**Implementation Framework and Tactics**\nThe email-centric campaign will deploy a three-phase approach over 4-6 weeks: Phase 1 (Week 1-2) launches with personalized congratulatory messages highlighting specific performance metrics and cohort rankings, followed by exclusive invitation to a \"Rising Stars\" recognition program. Phase 2 (Week 2-4) delivers value-added content including advanced training modules, one-on-one mentorship opportunities with top-performing senior agents, and early access to new product launches. Phase 3 (Week 4-6) culminates with exclusive benefit offerings such as enhanced commission structures, priority lead allocation, and invitation to executive roundtable sessions. Each email will feature personalized performance dashboards, peer comparison data, and clear calls-to-action that drive engagement with retention-focused touchpoints. The campaign will integrate with CRM systems to track engagement metrics and trigger automated follow-up sequences based on individual agent responses.\n\n**Expected Outcomes and Success Factors**\nSuccess will be measured through multiple key performance indicators: 100% retention of target agents through the campaign period and 6 months post-campaign, 80%+ email engagement rates, and 90%+ participation in offered exclusive programs. Secondary metrics include increased premium production (15% uplift expected), improved satisfaction scores (targeting movement from moderate to high satisfaction), and enhanced loyalty indicators such as referral generation and contract renewals. Critical success factors include executive sponsorship for exclusive benefits delivery, seamless integration between marketing automation and agent support systems, and rapid response capabilities for addressing individual agent concerns. The campaign's effectiveness will establish benchmarks for expanding this approach to larger high-performer segments, with potential ROI projected at 300-400% based on retained agent lifetime value versus acquisition costs for replacement talent.","messaging":{"primary_message":"Value recognition and exclusive benefits","emotional_hooks":["appreciation","exclusivity","long-term partnership","special recognition"],"key_benefits":["VIP status","premium services","priority support","exclusive products"],"tone":"appreciative, exclusive, professional","customization":"Premium messaging: Focus on sophisticated products and exclusive services","special_focus":"","sample_headlines":["You're Part of Our Elite Agent Network - Exclusive Opportunities Await","VIP Recognition: Unlock Premium Benefits Reserved for Top Performers","Your Success Story Continues - Special Offers Just for You"],"call_to_action":"Schedule your exclusive consultation today"},"channels":{"recommended_channels":{"digital":{"email":{"priority":"high","reasoning":"Direct, personalized communication"},"website_portal":{"priority":"medium","reasoning":"Self-service convenience"},"mobile_app":{"priority":"high","reasoning":"On-the-go access"}},"traditional":{"phone":{"priority":"high","reasoning":"Personal relationship building"},"direct_mail":{"priority":"medium","reasoning":"Tangible, memorable"},"fax":{"priority":"low","reasoning":"Legacy preference"}},"events":{"webinars":{"priority":"medium","reasoning":"Educational engagement"},"conferences":{"priority":"medium","reasoning":"Networking opportunities"},"training":{"priority":"high","reasoning":"Onboarding and skill development"}}},"primary_channel":"email","channel_sequence":["email","phone","website_portal","direct_mail"],"personalization_tips":["Use agent's actual AUM amount in messages","Reference their positive NPS experience"]},"timing":{"campaign_timeline":{"duration":"4-6 weeks","phases":[{"phase":"Awareness","duration":"1-2 weeks","goal":"Generate interest"},{"phase":"Consideration","duration":"2-3 weeks","goal":"Build engagement"},{"phase":"Decision","duration":"1 week","goal":"Drive action"}]},"optimal_timing":{"best_days":["Tuesday","Wednesday","Thursday"],"best_times":["9:00 AM - 11:00 AM","2:00 PM - 4:00 PM"],"avoid_times":["Early morning","Late evening","Lunch hours"]},"seasonal_recommendations":{"best_months":["January","February","September","October"],"avoid_months":["November","December","June","July"],"reasoning":"Based on agent tenure and business cycle"},"follow_up_schedule":[{"timing":"Immediate","type":"Confirmation"},{"timing":"1 day","type":"Engagement"},{"timing":"1 week","type":"Value offer"},{"timing":"2 weeks","type":"Push messaging"},{"timing":"1 month","type":"Relationship building"}]},"budget":{"total_budget":2500,"budget_per_agent":500,"rationale":"Premium budget justified by high AUM potential","allocation":{"creative_development":{"percentage":20,"amount":500.0},"channel_execution":{"percentage":60,"amount":1500.0},"measurement_tracking":{"percentage":10,"amount":250.0},"optimization":{"percentage":10,"amount":250.0}},"roi_expectations":{"expected_revenue":7500,"roi_percentage":200,"payback_period":"90-120 days"},"budget_optimization_tips":["Focus 70% budget on highest-performing channels","Use A/B testing to optimize message performance","Implement automated follow-up to reduce manual costs"]},"success_metrics":{"objective":"retention","primary_kpi":"Retention Rate","target_rate":"90%+","secondary_kpis":["Renewal Rate: 85%+","Satisfaction Score: 8.5+","Advocacy Score: 40%+"],"engagement_metrics":["Email Open Rate: 25%+","Phone Answer Rate: 60%+","Portal Login Increase: 30%+"],"measurement_timeline":"30, 60, 90 days","reporting_frequency":"Weekly during campaign, Monthly post-campaign","baseline_metrics":{"current_engagement_rate":"12%","average_response_time":"2-3 days","satisfaction_baseline":"75%","monthly_interaction_frequency":"2-3 times"}},"implementation_plan":[{"week":1,"phase":"Setup & Launch","activities":["Finalize messaging and creative assets","Set up campaign tracking and analytics","Segment agent lists by channel preference","Launch initial awareness phase"]},{"week":2,"phase":"Awareness Building","activities":["Deploy multi-channel awareness campaigns","Monitor engagement metrics","Begin personalized outreach","Gather initial feedback"]},{"week":-1,"phase":"Engagement & Conversion","activities":["Intensify personalized messaging","Conduct direct sales activities","Provide additional value-added content","Track conversion metrics"]},{"week":-1,"phase":"Follow-up & Optimization","activities":["Follow up with non-responders","Optimize messaging based on results","Conduct final push activities","Begin relationship nurturing"]}]},"confidence_score":0.7}
