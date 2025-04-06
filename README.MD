# 🔤 Alphabet Learning Adventure

An interactive, voice-enabled application designed to help children learn the alphabet through engaging visuals and OpenAI's latest audio technology.

## 🌟 Features

- **Interactive Letter Buttons**: Colorful, engaging buttons for each letter of the alphabet
- **Voice Narration**: High-quality voice explanations using OpenAI's TTS technology
- **Multiple Voice Options**: Six different voice personalities (Premium feature)
- **Phonetic Guidance**: Clear pronunciation guides and phonetic information
- **Example Words**: Visual representation of words starting with each letter
- **Practice Suggestions**: Interactive activities to reinforce learning
- **Mobile-Friendly**: Responsive design that works on tablets and mobile devices
- **Tips for Parents/Teachers**: Guidance for adults to enhance the learning experience
- **Freemium Model**: Free demo with A-F access, full alphabet with premium access

## 📋 Requirements

- Python 3.8+
- Streamlit
- OpenAI API Key
- Internet connection for API calls (first use only)

## 🚀 Quick Start

1. Clone this repository:
```bash
git clone https://github.com/your-username/alphabet-learning-adventure.git
cd alphabet-learning-adventure
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

4. Run the application:
```bash
streamlit run app.py
```

## 🔒 Access Model

The app uses a simple freemium model:

- **Free Demo**: Access to letters A-F with basic "nova" voice
- **Premium Access**: Full access to all 26 letters, 6 voices, and HD audio
- Purchase premium access on [Gumroad](https://lindsayhiebert.gumroad.com/l/alphabet-adventure)

## 🌐 Deployment

This app is designed for easy deployment to Streamlit Cloud:

1. Connect your GitHub repository to [Streamlit Cloud](https://streamlit.io/cloud)
2. Add your OpenAI API key as a secret
3. Deploy with one click

## 🏬 Feature Comparison

### Free Demo:
- Access to letters A-F only
- Basic "nova" voice only
- Standard audio quality
- Limited settings options

### Premium Version ($1.99):
- Access to all 26 letters of the alphabet
- Six different voice options (nova, alloy, echo, fable, onyx, shimmer)
- HD audio quality option
- Detailed phonetic information and JSON data

## 👤 Author

**Lindsay Hiebert**

- LinkedIn: [lindsayhiebert](https://www.linkedin.com/in/lindsayhiebert/)
- GitHub: [your-github-username](https://github.com/your-github-username)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
