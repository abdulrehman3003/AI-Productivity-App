import json
from typing import List, Optional, Dict
from datetime import datetime
import re
from textblob import TextBlob  # Simple NLP analysis
import numpy as np

class GraniteService:
    def __init__(self, api_key: Optional[str] = None):
        # No API key needed for local version
        pass

    def generate_insights(self, tasks: List[Dict]) -> Dict:
        try:
            print("\n" + "="*40)
            print("Starting insights generation with tasks:", len(tasks))
            
            if not tasks:
                print("No tasks found")
                return self._get_empty_response()
            
            # Convert tasks to safe format with default values
            safe_tasks = []
            for task in tasks:
                safe_tasks.append({
                    'title': str(task.get('title', 'Untitled Task')),
                    'priority': str(task.get('priority', 'Low')).capitalize(),
                    'deadline': task.get('deadline', ''),
                    'status': str(task.get('status', 'pending')).lower(),
                    'description': str(task.get('description', ''))
                })
            
            print("Sample safe task data:", safe_tasks[:1])

            # Initialize analysis with proper defaults
            analysis = {
                "total_tasks": len(safe_tasks),
                "completed_tasks": 0,
                "priorities": {"High": 0, "Medium": 0, "Low": 0},
                "deadlines": [],
                "deadline_clustering": 0
            }

            # Process tasks using safe data
            deadline_counts = {}
            for task in safe_tasks:
                # Priority analysis
                priority = task['priority']
                if priority in analysis["priorities"]:
                    analysis["priorities"][priority] += 1
                
                # Deadline analysis
                if task['deadline']:
                    analysis["deadlines"].append(task['deadline'])
                    deadline_counts[task['deadline']] = deadline_counts.get(task['deadline'], 0) + 1
                
                # Completion status
                if task['status'] == 'completed':
                    analysis["completed_tasks"] += 1

            # Calculate deadline clustering
            if deadline_counts:
                analysis["deadline_clustering"] = max(deadline_counts.values())

            print("Final analysis data:", analysis)

            # Generate insights components
            insights = {
                "productivity_analysis": self._generate_productivity_analysis(analysis),
                "recommendations": self._generate_recommendations(analysis),
                "time_management": self._analyze_time_management(analysis["deadlines"]),
                "priority_distribution": analysis["priorities"],
                "task_breakdown": self._generate_task_breakdown(safe_tasks),
                "completion_trends": self._generate_completion_trends(tasks),
                "deadline_clustering": analysis["deadline_clustering"]
            }

            return insights
        
        except Exception as e:
            print(f"Insights generation failed: {str(e)}")
            return self._get_fallback_response()

    def _generate_productivity_analysis(self, analysis: Dict) -> str:
        total = analysis["total_tasks"]
        completed = analysis["completed_tasks"]
        high_priority = analysis["priorities"]["High"]
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        high_priority_ratio = (high_priority / total * 100) if total > 0 else 0
        
        return f"""📈 **Productivity Overview**
        - Task completion: {completion_rate:.1f}%
        - High priority tasks: {high_priority} ({high_priority_ratio:.1f}%)
        - Total tasks: {total}"""

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        recs = []
        
        # Priority-based recommendations
        if analysis["priorities"]["High"] > analysis["total_tasks"] / 2:
            recs.append("⚠️ Balance priorities - High priority tasks exceed 50%")
        
        # Deadline-based recommendations
        unique_deadlines = len(set(analysis["deadlines"]))
        if unique_deadlines < len(analysis["deadlines"]):
            recs.append("📅 Spread out deadlines - Multiple tasks share due dates")
        
        # General recommendations
        recs.extend([
            "📋 Break large tasks into smaller steps",
            "⏳ Use time blocking for focused work",
            "🔄 Review priorities weekly",
            "🎯 Focus on high-impact tasks first"
        ])
        
        return recs

    def _analyze_time_management(self, deadlines: List) -> str:
        if not deadlines:
            return "⏳ No deadlines set - Add deadlines for better planning"
        
        unique_dates = len(set(deadlines))
        if unique_dates < len(deadlines):
            return f"⚠️ Deadline clustering - {len(deadlines)-unique_dates} overlapping due dates"
        
        return "✅ Well-distributed deadlines - Good workload balance"

    def _format_priority_distribution(self, priorities: Dict) -> Dict:
        """
        Format priority distribution as a dictionary for charting.
        """
        return priorities  # Return the raw dictionary instead of formatting as a string

    def _get_fallback_response(self) -> Dict:
        return {
            "productivity_analysis": "Insights generation failed - Using fallback data",
            "recommendations": [
                "Check your task details",
                "Verify deadline formats",
                "Ensure priorities are set"
            ],
            "time_management": "Could not analyze time management",
            "priority_distribution": "Priority data unavailable"
        }

    def _date_score(self, deadline: Optional[str]) -> int:
        if not deadline:
            return 9999
        try:
            from datetime import datetime
            days_left = (datetime.strptime(deadline, '%Y-%m-%d').date() - datetime.today().date()).days
            return max(0, days_left)
        except:
            return 9998  # Invalid dates get lower priority

    def prioritize_tasks(self, tasks: list) -> list:
        """AI-powered task prioritization considering multiple factors"""
        try:
            return sorted(
                tasks,
                key=lambda x: (
                    {'High': 0, 'Medium': 1, 'Low': 2}[x.get('priority', 'Low')],
                    self._date_score(x.get('deadline')),
                    -1 * (x.get('created_at', '') != ''),  # Newer tasks first
                    {'Work': 0, 'Study': 1, 'Health': 2, 'Personal': 3}[x.get('category', 'Personal')]
                )
            )
        except Exception as e:
            print(f"Prioritization error: {str(e)}")
            return sorted(tasks, key=lambda x: x.get('deadline', ''))

    def _create_prioritization_prompt(self, tasks: list) -> str:
        return f"Analyze and prioritize these tasks: {tasks}"
        
    def _create_insights_prompt(self, tasks: list) -> str:
        return f"Generate productivity insights for these tasks: {tasks}"

    def parse_natural_language(self, text: str) -> Dict:
        try:
            # Example implementation using regex (replace with actual Granite integration)
            patterns = {
                'time': r'\b(at|by)\s+(\d{1,2}(?:[:]\d{2})?\s*(?:AM|PM)?)\b',
                'date': r'\b(tomorrow|today|next week|\d{4}-\d{2}-\d{2})\b',
                'priority': r'\b(urgent|important|critical)\b'
            }
            
            return {
                'title': re.sub(r'\b(?:at|by|tomorrow|urgent)\b', '', text).strip(),
                'deadline': self._parse_date(re.findall(patterns['date'], text)),
                'priority': "High" if re.search(patterns['priority'], text) else "Medium"
            }
        except Exception as e:
            print(f"NLU Error: {str(e)}")
            return {'title': text}

    def _generate_task_recommendation(self, task: Dict) -> Optional[str]:
        description = task['description'].lower()
        title = task['title'].lower()
        
        # Simple keyword-based recommendations
        keywords = {
            'meeting': "⏰ Schedule in calendar with agenda",
            'email': "📧 Draft template first, then personalize",
            'review': "🔍 Break into sections for focused analysis",
            'project': "📂 Create milestone checklist",
            'call': "📞 Prepare talking points beforehand",
            'report': "📊 Start with data collection first"
        }
        
        for kw, rec in keywords.items():
            if kw in description or kw in title:
                return f"{task['title']}: {rec}"
        
        # Fallback based on priority
        if task.get('priority') == 'High':
            return f"{task['title']}: 🚨 Break into smaller steps and start immediately"
        
        return None 

    def _analyze_task_description(self, description: str) -> str:
        """Generate AI-powered task completion tips"""
        analysis = TextBlob(description)
        
        # Detect task type based on keywords
        keywords = {
            'meeting': "Schedule in calendar with clear agenda",
            'review': "Break into sections and allocate time per part",
            'email': "Draft key points first before writing full email",
            'call': "Prepare talking points and questions in advance",
            'project': "Create milestone checklist with deadlines",
            'report': "Start with data collection and outline structure"
        }
        
        for kw, tip in keywords.items():
            if kw in description.lower():
                return tip
        
        # Fallback analysis
        if analysis.sentiment.polarity < -0.1:
            return "Break this into smaller, manageable steps"
        if len(description.split()) > 50:
            return "Consider breaking this into sub-tasks"
        
        return "Focus on one step at a time - you've got this!" 

    def get_task_insights(self, task: Dict) -> Dict:
        """Generate insights for a single task"""
        try:
            insights = {
                'recommendations': [],
                'description_analysis': self._analyze_task_description(task.get('description', ''))
            }
            
            # Priority-based tips
            if task.get('priority') == 'High':
                insights['recommendations'].append("🚨 High priority - Schedule dedicated time for this task")
            elif task.get('priority') == 'Medium':
                insights['recommendations'].append("🕒 Medium priority - Plan for later in the day")
            else:
                insights['recommendations'].append("🐢 Low priority - Batch with similar tasks")
                
            # Deadline analysis
            if task.get('deadline'):
                days_left = self._days_until_deadline(task['deadline'])
                if days_left < 3:
                    insights['recommendations'].append(f"⏳ Due in {days_left} days - Prioritize completion")
                    
            return insights
            
        except Exception as e:
            print(f"Task insights error: {str(e)}")
            return {
                'recommendations': ["Could not generate specific recommendations"],
                'description_analysis': "Analysis failed"
            }

    def _days_until_deadline(self, deadline: str) -> int:
        from datetime import datetime
        try:
            due_date = datetime.strptime(deadline, '%Y-%m-%d').date()
            today = datetime.today().date()
            return (due_date - today).days
        except:
            return 9999 

    def _generate_task_breakdown(self, tasks: List[Dict]) -> List[Dict]:
        breakdown = []
        for task in tasks:
            if task['description']:
                analysis = self._analyze_task_description(task['description'])
                if analysis:
                    breakdown.append({
                        'title': task['title'],
                        'recommendation': analysis
                    })
        return breakdown 

    def generate_task_guide(self, task: Dict) -> Dict:
        try:
            # Extract task components
            title = task.get('title', '').lower()
            description = task.get('description', '').lower()
            category = task.get('category', '').lower()
            priority = task.get('priority', 'Low')
            deadline = task.get('deadline')
            
            # Perform deep analysis
            analysis = {
                'keywords': self._extract_key_phrases(description),
                'complexity': self._assess_complexity(description),
                'collaboration_needs': self._detect_collaboration(description),
                'research_needs': self._detect_research_requirements(description),
                'tools': self._identify_tools(description)
            }
            
            # Build comprehensive guide
            guide = {
                'title': f"Complete: {task.get('title', 'Task')}",
                'steps': self._generate_steps(analysis, priority, deadline),
                'time_management': self._generate_time_strategy(analysis, priority, deadline),
                'tools': analysis['tools'],
                'resources': self._identify_resources(description),
                'frameworks': self._suggest_frameworks(analysis),
                'checklist': self._create_checklist(analysis),
                'potential_challenges': self._anticipate_challenges(analysis)
            }
            
            return guide
            
        except Exception as e:
            print(f"Guide generation error: {str(e)}")
            return self._get_fallback_guide()

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract important phrases using TextBlob"""
        blob = TextBlob(text)
        return [np.lemmatize() for np in blob.noun_phrases if len(np.split()) > 1]

    def _assess_complexity(self, text: str) -> str:
        word_count = len(text.split())
        sentence_count = len(TextBlob(text).sentences)
        return "High" if word_count > 100 or sentence_count > 10 else "Medium"

    def _detect_collaboration(self, text: str) -> bool:
        return bool(re.search(r'\b(team|collaborate|partner|review)\b', text))

    def _identify_tools(self, text: str) -> List[str]:
        tools = []
        # Development tools
        if re.search(r'\b(code|program|develop|script)\b', text):
            tools.extend(["IDE (VSCode/PyCharm)", "Git", "Debugging Tools"])
        # Design tools
        if re.search(r'\b(design|ui|ux|mockup)\b', text):
            tools.extend(["Figma", "Adobe XD", "Sketch"])
        # Analysis tools
        if re.search(r'\b(analyze|data|report|research)\b', text):
            tools.extend(["Excel/Sheets", "Tableau", "Python Pandas"])
        return list(set(tools))

    def _generate_steps(self, analysis: Dict, priority: str, deadline: Optional[str]) -> List[str]:
        steps = []
        # Initial preparation
        steps.append(f"1. Clarify objectives ({analysis['keywords'][0]} first)")
        
        # Research phase
        if analysis['research_needs']:
            steps.append("2. Conduct background research using:")
            steps.append("   - Academic databases")
            steps.append("   - Industry reports")
        
        # Collaboration planning
        if analysis['collaboration_needs']:
            steps.append("3. Schedule team alignment meeting")
        
        # Implementation steps
        steps.append("4. Create detailed action plan with milestones")
        
        # Review phase
        steps.append("5. Conduct quality assurance checks")
        
        # Finalization
        steps.append("6. Prepare final deliverables package")
        
        return steps

    def _generate_time_strategy(self, analysis: Dict, priority: str, deadline: Optional[str]) -> Dict:
        strategy = {
            'technique': "Pomodoro (25min work + 5min breaks)",
            'daily_allocation': "2-3 hours" if priority == 'High' else "1 hour",
            'weekly_plan': []
        }
        
        if analysis['complexity'] == 'High':
            strategy['technique'] = "Time Blocking (dedicated 2hr slots)"
            strategy['daily_allocation'] = "3-4 hours"
        
        if deadline:
            days_left = self._days_until_deadline(deadline)
            strategy['milestones'] = self._create_milestones(days_left, analysis['complexity'])
        
        return strategy

    def _suggest_frameworks(self, analysis: Dict) -> List[str]:
        frameworks = []
        if analysis['complexity'] == 'High':
            frameworks.append("Agile Methodology (Sprint Planning)")
        if analysis['research_needs']:
            frameworks.append("SWOT Analysis")
        if analysis['collaboration_needs']:
            frameworks.append("RACI Matrix")
        return frameworks

    def _create_checklist(self, analysis: Dict) -> List[str]:
        # Implementation of _create_checklist method
        pass

    def _anticipate_challenges(self, analysis: Dict) -> List[str]:
        challenges = []
        if analysis['complexity'] == 'High':
            challenges.append("Requires deep focus periods")
        if analysis['collaboration_needs']:
            challenges.append("Coordination with multiple stakeholders")
        if len(analysis['tools']) > 3:
            challenges.append("Learning curve for multiple tools")
        return challenges

    def _detect_research_requirements(self, text: str) -> bool:
        return bool(re.search(r'\b(research|data|analyze|study|survey)\b', text))

    def _create_milestones(self, days_left: int, complexity: str) -> List[str]:
        # Implementation of _create_milestones method
        pass

    def _identify_resources(self, description: str) -> List[str]:
        """Identify potential resources needed based on description"""
        resources = []
        
        # Detect document references
        if re.search(r'\b(document|file|report)\b', description):
            resources.append("Related documents/files")
        
        # Detect research needs
        if re.search(r'\b(research|data|study)\b', description):
            resources.extend(["Research papers", "Data sources"])
        
        # Detect tool requirements
        if re.search(r'\b(software|tool|app)\b', description):
            resources.append("Specialized software/tools")
        
        # Detect collaboration needs
        if re.search(r'\b(team|colleague|partner)\b', description):
            resources.append("Team collaboration")
        
        return list(set(resources))  # Remove duplicates

    def _get_fallback_guide(self) -> Dict:
        return {
            'error': "Could not generate detailed guide",
            'steps': [],
            'time_management': {},
            'tools': [],
            'resources': ["General reference materials"],
            'frameworks': [],
            'checklist': [],
            'potential_challenges': []
        } 

    def _generate_completion_trends(self, tasks: List[Dict]) -> Dict:
        """
        Generate completion trends over time.
        """
        trends = {}
        for task in tasks:
            if task['status'] == 'completed':
                completion_date = task.get('completion_date', datetime.today().strftime('%Y-%m-%d'))
                week = f"Week {datetime.strptime(completion_date, '%Y-%m-%d').isocalendar()[1]}"
                if week not in trends:
                    trends[week] = 0
                trends[week] += 1
        
        # Ensure the trends are sorted by week
        sorted_trends = dict(sorted(trends.items(), key=lambda x: int(x[0].split()[1])))
        return sorted_trends

    def _get_empty_response(self) -> Dict:
        return {
            "productivity_analysis": "No tasks added yet",
            "recommendations": [],
            "time_management": "No tasks added yet",
            "priority_distribution": "No tasks added yet",
            "task_breakdown": [],
            "completion_trends": {}
        }

    def _get_fallback_response(self) -> Dict:
        return {
            "productivity_analysis": "Insights generation failed - Using fallback data",
            "recommendations": [
                "Check your task details",
                "Verify deadline formats",
                "Ensure priorities are set"
            ],
            "time_management": "Could not analyze time management",
            "priority_distribution": "Priority data unavailable",
            "task_breakdown": [],
            "completion_trends": {}
        } 

    def generate_task_steps(self, task: Dict) -> List[str]:
        """
        Generate AI-powered task completion steps using IBM Granite.
        """
        try:
            description = task.get('description', '')
            if not description:
                return [
                    "▸ Review the task details",
                    "▸ Break the task into smaller steps",
                    "▸ Execute each step systematically"
                ]
            
            # Create a prompt for IBM Granite
            prompt = f"""Generate detailed steps to complete this task based on its description:
            Task Description: {description}
            
            Provide 5-7 clear, actionable steps to complete this task effectively.
            Format each step as a bullet point starting with "▸".
            """
            
            # Call IBM Granite API (replace with actual API call)
            # response = self.granite_api.generate(prompt)
            # steps = response.get('steps', [])
            
            # Simulate IBM Granite response (replace with actual API call)
            steps = [
                "▸ Review the task requirements and objectives",
                "▸ Break down the task into smaller sub-tasks",
                "▸ Prioritize sub-tasks based on importance and deadline",
                "▸ Allocate specific time blocks for each sub-task",
                "▸ Execute the sub-tasks in order of priority",
                "▸ Review and refine completed work",
                "▸ Submit or finalize the task before the deadline"
            ]
            
            # Ensure we have at least 3 steps
            if len(steps) < 3:
                steps = [
                    "▸ Review the task details",
                    "▸ Break the task into smaller steps",
                    "▸ Execute each step systematically"
                ]
            
            return steps
        except Exception as e:
            print(f"Error generating task steps: {str(e)}")
            return [
                "▸ Review the task details",
                "▸ Break the task into smaller steps",
                "▸ Execute each step systematically"
            ] 