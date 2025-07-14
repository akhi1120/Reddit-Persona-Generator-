# Reddit-Persona-Generator-
# Reddit Persona Generator

A Python script that fetches a Reddit user’s posts and comments via PRAW, feeds them to OpenAI GPT-4, and writes out a qualitative user persona with citations.

## Overview

This tool:

1. **Authenticates** to Reddit (script‐type app, password grant)  
2. **Fetches** up to 100 recent posts & comments for any public username  
3. **Prompts** OpenAI GPT-4 to craft a user persona (interests, traits, values)  
4. **Saves** the persona to a text file in `sample_output/`

##  Prerequisites

- Python 3.8+  
- A Reddit account (2FA **disabled** for script login)  
- A Reddit “script” app (client ID & secret)  
- An OpenAI API key (for GPT-4 calls)  

##  Installation
pip install -r requirements.txt

##  Create & activate a virtual environment:
python -m venv reddit-env
.\reddit-env\Scripts\activate
pip install -r requirements.txt

##  Usage
python main.py

## What It Does?

Takes a Reddit user profile URL (e.g. https://www.reddit.com/user/kojied/).

Authenticates to Reddit via PRAW in “script” mode using your Reddit username/password.

Fetches up to 100 of the user’s most recent posts and comments.

Sends a combined snippet of that content to OpenAI GPT-4, asking it to craft a qualitative “user persona” (interests, behavior, personality, values) with citations back to specific lines.

Saves the generated persona to a text file in sample_output/<username>_persona.txt.

