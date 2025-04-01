# Code Review Assistant using Portialabs SDK

## Project Overview

This project implements an **AI-powered code review assistant** using the **Portialabs SDK**. It allows users to submit code snippets and receive detailed reviews in three categories:
- **General Review** (code quality, best practices, potential bugs)
- **Security Review** (security vulnerabilities, input validation)
- **Performance Review** (time complexity, space complexity, optimization)

## Features
- **AI-powered code reviews**: Get detailed feedback on your code's quality, security, and performance.
- **Customizable reviews**: Select the type of review that best suits your needs (general, security, or performance).
- **User-friendly interface**: Code snippets are displayed with syntax highlighting, and reviews are formatted for easy reading.

## What I Liked About Portialabs SDK

1. **Ease of Integration**: 
   - The SDK was easy to set up and integrate into my project. I was able to connect to Portialabs’ services with minimal configuration and start generating code reviews quickly.

2. **AI-Powered Feedback**:
   - Portialabs provided deep insights into the code. The reviews identified issues like security vulnerabilities, performance bottlenecks, and areas for improvement. The feedback was detailed and actionable.

3. **Clear Documentation**:
   - The SDK's documentation was clear and comprehensive, with plenty of examples that helped me get up to speed quickly.

## Challenges Encountered

1. **Parsing Responses**:
   - Review responses sometimes contained unstructured text, making it a bit tricky to display them in a user-friendly format. I had to experiment with formatting to ensure the output was readable.

2. **Rate Limiting**:
   - Handling rate limits was a challenge. The SDK didn't offer built-in retry logic, so I implemented exponential backoff (waiting progressively longer between retries) to handle rate-limit errors.

3. **Error Handling**:
   - Some error messages were not as descriptive as expected, which made debugging a bit more time-consuming. I had to rely on logs to figure out the source of some issues.

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/code-review-assistant.git
   cd code-review-assistant
2. Install the required dependencies:

Copy
pip install -r requirements.txt

3. Set up your environment variables:
Create a .env file and add your Portialabs API key and any other necessary configuration.

4. Run the application:
Copy
python main.py
Follow the on-screen prompts to input code and choose the type of review.
