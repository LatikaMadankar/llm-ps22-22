# Flashcard Generator

An LLM-based study tool that converts study notes into question-answer flashcards for quick revision.

## Problem Statement

Students often need quick revision material from lengthy study notes. This project uses a Large Language Model (LLM) to automatically convert notes into useful question-answer flashcards.

## Features

- Convert study notes into flashcards using Gemini API
- Generate 3, 5, 7, or 10 flashcards
- Question-answer format
- Reveal answer functionality
- Previous and Next navigation
- Progress indicator
- Download flashcards as CSV
- Modern Streamlit interface
- JSON structured LLM output
- Pandas DataFrame processing

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- Pandas
- JSON
- python-dotenv

## Project Flow

Study Notes
      ↓
Prompt Engineering
      ↓
Gemini LLM
      ↓
JSON Response
      ↓
Pandas DataFrame
      ↓
Flashcard UI
      ↓
CSV Download

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FlashcardGenerator