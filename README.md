# 🌍 Travel Planner AI – Intelligent Trip Recommendation System

An AI-powered travel planning application that recommends personalized destinations, itineraries, and travel insights based on user preferences. This project demonstrates end-to-end implementation of a machine learning–driven recommendation system with an interactive web interface.

# 🎯 Quick Links

- Overview

- Features

- Installation

- Quick Start

- Web App Features

- Implementation Details

- Model Architecture

- Dataset Information

- Example Outputs

- Improvements

- Troubleshooting

# 📌 Overview

Travel Planner AI is a smart travel recommendation system that helps users discover ideal travel destinations based on budget, interests, duration, and travel style.

The system combines:

- Machine Learning recommendation logic

- Rule-based filtering

- Interactive Streamlit web application

- User preference customization

- Real-time trip planning output

# 🚀 Key Achievements

- ✅ Personalized destination recommendations
- ✅ Budget-based filtering system
- ✅ Interest-based trip matching (adventure, relaxation, culture, etc.)
- ✅ Interactive Streamlit web app
- ✅ Clean and modular project structure
- ✅ Ready-to-run application
- ✅ Expandable dataset design

# 📁 Project Structure

```
travel-planner-ai/
│
├── app.py                      # Streamlit web application
├── model.py                    # Recommendation logic
├── data/
│   └── destinations.csv        # Travel dataset
├── utils.py                    # Helper functions
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

### ✨ Features
### 🧠 AI Recommendation Features

- Content-based recommendation system

- Budget filtering (Low / Medium / High)

- Duration-based suggestions

- Interest matching

- Location type filtering (Beach, Mountain, City, Nature)

- Ranking system for best matches

### 🌐 Web Application Features

### 📝 User Inputs

- Budget Range

- Travel Duration (1–14 days)

- Travel Style:

- Adventure

- Relaxation

- Cultural

- Luxury

- Nature

- Preferred Climate

- International or Domestic

### ⚙️ Smart Filters

- Remove destinations exceeding budget

- Filter by climate compatibility

- Match activity types with interests

- Rank based on similarity score

### 📊 Output Features

- Top 3–5 recommended destinations

- Estimated budget breakdown

- Suggested itinerary highlights

- Activity recommendations

- Travel tips

- Interactive UI with clean layout

### 🛠 Installation

- Prerequisites

- Python 3.8+

- pip

- 4GB RAM minimum

Step-by-Step Setup
# Clone repository
git clone <your-repo-url>
cd travel-planner-ai

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
▶️ Quick Start
Run the Web Application
streamlit run app.py

Then open:

http://localhost:8501

### 🧠 Recommendation System Architecture
Current Architecture (Content-Based Filtering)
### Step 1: Data Preprocessing

- Clean destination dataset

- Normalize budget ranges

- Encode travel styles

- Structure activity tags

### Step 2: Feature Engineering

- Convert interests into weighted vectors

- Encode climate and location types

- Budget compatibility scoring

### Step 3: Matching Algorithm

- Compute similarity score

- Filter incompatible destinations

- Rank top results

### 🔎 Scoring Formula (Example)
Final Score =
  (Interest Match × 0.4) +
  (Budget Compatibility × 0.3) +
  (Duration Match × 0.2) +
  (Climate Preference × 0.1)
### 📊 Dataset Information

Destinations Dataset

- Format: CSV

- Fields:

- Destination Name

- Country

- Budget Category

- Recommended Duration

- Climate

- Travel Style Tags

- Popular Activities

Example Entry:

Destination	Budget	Style	Climate	Duration
Bali	Medium	Relaxation, Nature	Tropical	5-7 days
🌍 Example Outputs
# Example 1

- User Input:

- Budget: Medium

- Duration: 5 days

- Style: Relaxation

- Climate: Tropical

- Recommended Destinations:

- Bali

- Phuket

- Maldives

# Example 2

- User Input:

- Budget: Low

- Duration: 3 days

- Style: Cultural

- Climate: Moderate

- Recommended Destinations:

- Jaipur

- Istanbul

- Prague

### 🎨 Web App Interface Guide
- Left Panel – User Preferences

- Select Budget

- Choose Travel Style

- Set Duration Slider

- Select Climate

- Right Panel – Results

- Top Recommendations

- Trip Summary

- Estimated Cost

- Activities

- Travel Tips

# 🔧 System Requirements
- Requirement	Minimum	Recommended
- 
- RAM	4 GB	8+ GB
- 
- Disk Space	200 MB	500 MB
- 
- Python	3.8	3.11

# 🚀 Potential Improvements

# Model Enhancements

- Add collaborative filtering

- Use TF-IDF vectorization

- Integrate embedding-based similarity

- Add reinforcement learning for feedback

- Data Improvements

- Expand dataset to 1000+ destinations

- Add real-time API integration (weather, flights)

- Include seasonal pricing

- UI Enhancements

- Map visualization

- Itinerary PDF export

- Shareable trip link

- Save favorite destinations

- User login system

### 🧪 Future AI Upgrades

- Integrate GPT-based itinerary generation

- Flight + hotel price prediction

- Multi-city route optimization

- Conversational chatbot travel planner

### 🛠 Troubleshooting

- ModuleNotFoundError

- pip install -r requirements.txt

- Streamlit Not Running

- pip install --upgrade streamlit

- Dataset Not Found Error

### Ensure:

- data/destinations.csv

- exists in the project directory.

### ✅ Evaluation Criteria Met

✔️ Functional AI-based recommendation system

✔️ Clean architecture and modular code

✔️ Interactive and user-friendly UI

✔️ Expandable dataset and logic

✔️ Real-world practical application
