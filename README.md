# Medical Chatbot with LLaMA2 and WhatsApp

## Introduction

By using tools like Meta for Developers, Glitch, and Ngrok, we enable the connection of LLaMA2 (or any other AI model) with WhatsApp to provide automated solutions across various applications.

## Connecting LLaMA2 with WhatsApp

### Requirements
1. **Meta for Developers**: Create a business account to obtain a trial number and WhatsApp token.
2. **Glitch**: Set up an account on Glitch to manage WhatsApp requests and responses.
3. **Ngrok**: Configure a public link to expose the server through Glitch.

### Configuration
- Use the live URL provided by Glitch as the endpoint.
- Connect Ngrok within Glitch to expose the server publicly.

## The Idea Behind the Medical Chatbot

### Objective: Automated Medical Reporting
The primary goal of this chatbot is to facilitate automated medical report creation. Through a series of structured questions, the chatbot gathers necessary information from the user and, upon completion, generates a detailed report to send to medical professionals.

#### Functionality
- **Interactive questions**: The user answers questions about symptoms and medical details.
- **Report generation**: After the questionnaire is completed, the chatbot creates a PDF report with the provided information.
  
## Demonstration

### Question Flow
- The chatbot asks specific questions to gather necessary user information.
- If the user has questions during the process, they can ask intermediate questions, which LLaMA2 will answer. Once resolved, the question flow resumes.

### Final Script
Upon completing the questions, the script passes the gathered information to LLaMA2 along with the user’s context, enabling it to generate a comprehensive report.

## Adaptability and Future

### Code Adaptability
The chatbot is highly adaptable, allowing it to be adjusted for:
- Writing restaurant reviews.
- Filling out forms for complaints, security reports, vehicle inspections, and more.
- Assisting with inventory management in restaurants and completing protocols and guidelines.

### Current and Future Enhancements
- **Automatic reminders**: Send reminders to take medications at specified times.
- **Integration with Google Calendar**: Track medical appointments and prescription renewals.
- **Medication inventory management**: Monitor the number of pills remaining in each bottle.
- **Medical information fine-tuning**: Enhance the chatbot’s database to respond to common questions, providing detailed information on medications, dosages, side effects, interactions, and storage.

### Demo:

## Conclusion

The medical chatbot with LLaMA2 not only simplifies medical report creation but is also adaptable for other applications. With future enhancements, the system will become even more useful and precise, offering reminders, personalized responses, and support for safe medication use.
