import os
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

# Mock LangChain components to avoid dependency issues
class MockPromptTemplate:
    def __init__(self, template, input_variables, partial_variables=None):
        self.template = template
        self.input_variables = input_variables
        self.partial_variables = partial_variables or {}
        
    def format(self, **kwargs):
        result = self.template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        for key, value in self.partial_variables.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        return result

class MockLLM:
    def __init__(self, api_key=None, temperature=0.7):
        self.api_key = api_key
        self.temperature = temperature
    
    def __call__(self, prompt):
        # Mock response generation based on prompt
        if "analyze" in prompt.lower() or "resume" in prompt.lower():
            return self._generate_analysis_response()
        elif "enhance" in prompt.lower():
            return self._generate_enhancement_response()
        else:
            return "I don't have a specific response for this prompt."
    
    def _generate_analysis_response(self):
        return """
        {"suggestions": ["Focus on quantifiable achievements", "Add more technical skills", "Improve formatting"], 
         "keywords": ["project management", "data analysis", "leadership"], 
         "score": 75.5, 
         "improvement_areas": ["Technical skills section", "Professional summary", "Achievement statements"]}
        """
    
    def _generate_enhancement_response(self):
        return """
        # Enhanced Resume
        
        ## Professional Summary
        Experienced software developer with 5+ years specializing in web applications and data processing solutions. Proven track record of delivering high-quality code and optimizing application performance.
        
        ## Skills
        - Programming: Python, JavaScript, TypeScript, SQL
        - Frameworks: React, Django, FastAPI
        - Tools: Git, Docker, AWS, CI/CD pipelines
        
        ## Experience
        ### Senior Developer | Tech Solutions Inc.
        - Implemented data processing pipeline that reduced report generation time by 65%
        - Led team of 5 developers to deliver client project 2 weeks ahead of schedule
        - Optimized database queries resulting in 40% performance improvement
        """

class MockLLMChain:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
    
    def run(self, **kwargs):
        # Format the prompt with the provided variables
        formatted_prompt = self.prompt.format(**kwargs)
        # Pass the formatted prompt to the LLM
        return self.llm(formatted_prompt)

class MockPydanticOutputParser:
    def __init__(self, pydantic_object):
        self.pydantic_object = pydantic_object
    
    def parse(self, text):
        # Create a mock instance of the output object
        import json
        try:
            data = json.loads(text.strip())
            return self.pydantic_object(**data)
        except:
            # If parsing fails, return a default instance
            return self.pydantic_object(
                suggestions=["Mock suggestion"],
                keywords=["Mock keyword"],
                score=50.0,
                improvement_areas=["Mock improvement area"]
            )
    
    def get_format_instructions(self):
        return "Return a JSON object with the following keys: suggestions, keywords, score, improvement_areas"

# Mock imports to replace LangChain
class MockLangChain:
    def __init__(self):
        self.llms = type('obj', (object,), {
            'OpenAI': MockLLM
        })
        self.chains = type('obj', (object,), {
            'LLMChain': MockLLMChain
        })
        self.prompts = type('obj', (object,), {
            'PromptTemplate': MockPromptTemplate
        })
        self.output_parsers = type('obj', (object,), {
            'PydanticOutputParser': MockPydanticOutputParser
        })

# Create mock langchain modules
langchain = MockLangChain()
from_import = __import__

# Override the import function to return mock objects
def __mock_import__(name, globals=None, locals=None, fromlist=(), level=0):
    if name == 'langchain.llms' and fromlist and 'OpenAI' in fromlist:
        return langchain.llms
    elif name == 'langchain.chains' and fromlist and 'LLMChain' in fromlist:
        return langchain.chains
    elif name == 'langchain.prompts' and fromlist and 'PromptTemplate' in fromlist:
        return langchain.prompts
    elif name == 'langchain.output_parsers' and fromlist and 'PydanticOutputParser' in fromlist:
        return langchain.output_parsers
    return from_import(name, globals, locals, fromlist, level)

# Mock classes
class ResumeAnalysisOutput:
    """Output schema for resume analysis"""
    def __init__(self, suggestions=None, keywords=None, score=0.0, improvement_areas=None):
        self.suggestions = suggestions or []
        self.keywords = keywords or []
        self.score = score
        self.improvement_areas = improvement_areas or []
    
    def dict(self):
        return {
            "suggestions": self.suggestions,
            "keywords": self.keywords,
            "score": self.score,
            "improvement_areas": self.improvement_areas
        }

class ResumeAI:
    """AI-powered resume enhancement"""
    
    def __init__(self):
        """Initialize the ResumeAI class"""
        self.llm = MockLLM(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.2)
        self.parser = MockPydanticOutputParser(pydantic_object=ResumeAnalysisOutput)
    
    def analyze_resume(self, resume_text: str, job_description: str = None) -> Dict:
        """Analyze resume and provide suggestions"""
        # Create prompt template
        template = """
        You are an expert resume reviewer with years of experience in HR and recruitment.
        Analyze the following resume and provide detailed feedback:
        
        Resume:
        {resume_text}
        
        {format_instructions}
        
        Provide a comprehensive analysis focusing on:
        1. Content and structure
        2. Skills and qualifications
        3. Achievements and impact
        4. Clarity and conciseness
        5. Keywords optimization
        
        """
        
        if job_description:
            template += """
            Also, compare the resume with the following job description and suggest improvements
            to better match the requirements:
            
            Job Description:
            {job_description}
            """
        
        # Create prompt
        prompt = MockPromptTemplate(
            template=template,
            input_variables=["resume_text"] + (["job_description"] if job_description else []),
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        # Create chain
        chain = MockLLMChain(llm=self.llm, prompt=prompt)
        
        # Run chain
        if job_description:
            result = chain.run(resume_text=resume_text, job_description=job_description)
        else:
            result = chain.run(resume_text=resume_text)
        
        # Parse result
        try:
            parsed_result = self.parser.parse(result)
            return parsed_result.dict()
        except Exception as e:
            print(f"Error parsing result: {e}")
            return {
                "suggestions": ["Error analyzing resume"],
                "keywords": [],
                "score": 0.0,
                "improvement_areas": ["Error analyzing resume"]
            }
    
    def enhance_resume(self, resume_text: str, job_description: str = None) -> str:
        """Enhance resume based on job description"""
        # Create prompt template
        template = """
        You are an expert resume writer with years of experience in HR and recruitment.
        Enhance the following resume to make it more effective and professional:
        
        Resume:
        {resume_text}
        
        """
        
        if job_description:
            template += """
            Optimize the resume for the following job description:
            
            Job Description:
            {job_description}
            
            Make sure to include relevant keywords from the job description.
            """
        
        template += """
        Return the enhanced resume in the same format as the original.
        Focus on:
        1. Using strong action verbs
        2. Quantifying achievements
        3. Highlighting relevant skills
        4. Improving clarity and conciseness
        5. Optimizing keywords
        
        Enhanced Resume:
        """
        
        # Create prompt
        prompt = MockPromptTemplate(
            template=template,
            input_variables=["resume_text"] + (["job_description"] if job_description else [])
        )
        
        # Create chain
        chain = MockLLMChain(llm=self.llm, prompt=prompt)
        
        # Run chain
        if job_description:
            result = chain.run(resume_text=resume_text, job_description=job_description)
        else:
            result = chain.run(resume_text=resume_text)
        
        return result
