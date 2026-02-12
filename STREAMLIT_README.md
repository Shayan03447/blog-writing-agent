# Streamlit UI for Blog Writing Agent

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional but recommended for research features
```

### 3. Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## ✨ Features

- **Modern, Attractive UI**: Beautiful gradient design with smooth animations
- **Real-time Progress Tracking**: See your blog being generated step-by-step
- **Error Handling**: Comprehensive error handling with helpful messages
- **Blog Preview**: View and download your generated blog post
- **Image Generation**: Automatically generates images for your blog (if needed)
- **Research Integration**: Automatically conducts web research when needed

## 📝 Usage

1. **Enter Your Topic**: Type your blog topic in the input field
   - Example: "Introduction to Python Decorators"
   - Example: "Latest AI Developments This Week"

2. **Configure Settings** (Optional):
   - Set the "As-of Date" for time-sensitive queries
   - Enable debug mode for troubleshooting

3. **Generate**: Click the "Generate Blog Post" button

4. **Wait for Generation**: The app will show progress through:
   - 🔀 Routing (determining if research is needed)
   - 🔍 Research (if needed)
   - 📋 Planning (creating blog outline)
   - ✍️ Writing (generating sections)
   - 🎨 Image Generation (if needed)
   - ✨ Finalization

5. **Download**: Once complete, download your blog as Markdown

## 🎨 UI Features

- **Status Cards**: Color-coded status indicators
- **Progress Bars**: Visual progress tracking
- **Responsive Design**: Works on different screen sizes
- **Dark Mode Support**: Adapts to your system theme

## ⚠️ Troubleshooting

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root directory

### API Key Errors
- Ensure your `.env` file is in the project root
- Verify your API keys are correct
- OpenAI API key is required; Tavily is optional but recommended

### Graph Execution Errors
- Check the debug console for detailed error messages
- Enable "Show Debug Info" in Advanced Settings for more details
- Ensure your OpenAI API key has sufficient credits

### Image Generation Issues
- Image generation uses Stable Diffusion (CPU mode)
- First run will download ~4GB model (one-time)
- Image generation may take 10-30 seconds per image
- If timeout occurs, blog will continue without images

## 🔧 Advanced Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for LLM operations
- `TAVILY_API_KEY`: Optional, enables web research features

### Streamlit Configuration

You can customize the app by modifying `app.py`:
- Change colors in the CSS section
- Adjust progress update intervals
- Modify error messages

## 📚 Project Structure

```
blog-writing-agent/
├── app.py                 # Streamlit UI application
├── Graph/
│   └── graph.py          # LangGraph workflow definition
├── nodes/                 # Processing nodes
│   ├── Route_Node.py     # Routing logic
│   ├── Worker_node.py    # Section writing
│   ├── orches_node.py    # Blog planning
│   ├── merging_node.py   # Content merging
│   └── image_generation_node.py  # Image generation
├── state/
│   └── State.py          # State schema
└── Schemas/              # Pydantic schemas
```

## 🎯 Tips for Best Results

1. **Be Specific**: More specific topics yield better results
2. **Use Research**: Topics requiring recent information work best with Tavily API
3. **Patience**: First image generation takes longer (model download)
4. **Review Output**: Always review and edit generated content

## 🐛 Known Issues

- Image generation on CPU can be slow (10-30 seconds per image)
- Large blog posts may take several minutes to generate
- First run requires downloading Stable Diffusion model (~4GB)

## 📞 Support

For issues or questions:
1. Check the debug console output
2. Enable "Show Debug Info" in Advanced Settings
3. Review error messages for specific guidance

---

**Enjoy creating amazing blog posts with AI! ✍️**
