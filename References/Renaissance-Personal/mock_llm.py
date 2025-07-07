class Response:
    """Mock Response object that mimics the structure of LLM API responses."""
    def __init__(self, content):
        self.content = content


class MockLLM:
    """
    A mock LLM class for testing purposes that returns predefined responses.
    """
    def __init__(self, response_mapping=None):
        """
        Initialize with optional mapping of inputs to responses.
        
        Args:
            response_mapping (dict, optional): Mapping of input patterns to responses
        """
        self.response_mapping = response_mapping or {}
        self.default_response = """
        I've analyzed the document and here are my actions:
        
        <execute>
        import pandas as pd
        import numpy as np
        
        # Create a sample dataframe
        df = pd.DataFrame({
            'A': np.random.randn(5),
            'B': np.random.randn(5)
        })
        
        print(df.describe())
        </execute>
        
        <new_section name="Analysis">
        I've created a sample dataframe and performed basic statistical analysis.
        </new_section>
        
        <append_section name="Findings">
        The dataframe shows random normally distributed values in columns A and B.
        </append_section>
        """
        
    def invoke(self, prompt):
        """
        Invoke the mock LLM with a prompt.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            Response: A Response object containing the content
        """
        # Check if any key in response_mapping is contained in the prompt
        for key, response in self.response_mapping.items():
            if key in prompt:
                return Response(response)
        
        # Return default response if no match
        return Response(self.default_response)