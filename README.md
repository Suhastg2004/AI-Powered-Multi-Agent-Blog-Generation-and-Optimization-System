# AI-Powered Blog Generation System

This project provides an AI-powered solution for small and medium-sized businesses (SMBs) to automate the generation of marketing blogs. The system utilizes a multi-agent framework powered by Microsoft Autogen, with **Perplexity AI** for research, **DALL·E** for image generation, and **Azure OpenAI GPT-4o** as the primary language model to generate optimized blog content.

## Features

- **Automated Blog Topic Generation**: The system automatically suggests unique blog topics based on the business profile, using advanced AI models.
- **Research Integration**: **Perplexity AI** is used for researching the suggested topics and generating relevant content.
- **AI-Generated Content**: The **Azure OpenAI GPT-4o** LLM generates high-quality blog content from the research material.
- **Image Generation**: The system uses **DALLE-3** to generate relevant images based on blog keywords to accompany the content.
- **Multi-Agent Workflow**: A custom multi-agent system powered by **Microsoft Autogen** coordinates between research, writing, and design agents to produce a comprehensive and formatted blog.

## Technologies Used

- **Microsoft Autogen**: Multi-agent framework to coordinate different roles (researcher, writer, designer).
- **Perplexity AI**: For topic research and content exploration.
- **DALL·E**: For generating images based on blog content.
- **Azure OpenAI GPT-4o**: Main LLM for generating the blog content.
- **Python**: The core programming language for the project.

## Installation

To install and run the project locally, follow the steps below:

### Prerequisites

- Python 3.7+
- Required API keys for **Azure OpenAI GPT-4o**, **Perplexity AI**, and **DALL·E**.

### Steps to Set Up

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/blog-generation-system.git
   cd blog-generation-system
