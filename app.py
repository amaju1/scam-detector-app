import streamlit as st
import time
import torch
import torch.nn as nn
import json
import re

# ==========================================
# 1. THE DEEP LEARNING MODEL DEFINITION
# ==========================================
class ScamDetectionLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_dim=100, hidden_dim=64, output_dim=1):
        super(ScamDetectionLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        # Matches the exact 1-layer Bi-LSTM setup you just trained locally
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=1, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)
        
    def forward(self, text, text_lengths):
        embedded = self.embedding(text)
        packed_embedded = nn.utils.rnn.pack_padded_sequence(
            embedded, text_lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        packed_output, (hidden, cell) = self.lstm(packed_embedded)
        features = torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim=1)
        return self.fc(features)

# ==========================================
# 2. CACHED MODEL LOADING FUNCTION
# ==========================================
@st.cache_resource # Keeps the model in RAM so it stays lightning fast on your phone
def load_trained_ai_engine():
    """
    Reads the vocabulary index file and reconstructs the PyTorch 
    network with the learned weights you trained on your desktop.
    """
    try:
        # Load your training vocabulary mapping mapping
        with open("vocabulary.json", "r") as f:
            vocab = json.load(f)
            
        vocab_size = len(vocab)
        model = ScamDetectionLSTM(vocab_size=vocab_size)
        
        # Load the binary weights file you just generated
        model.load_state_dict(torch.load("scam_detector_weights.pt", map_location=torch.device('cpu')))
        model.eval() # Turns off training nodes for fast evaluation
        
        return model, vocab
    except FileNotFoundError:
        # Emergency fallback if your repository files haven't synced yet
        return None, None

# Run the background file loader
model, vocabulary = load_trained_ai_engine()

# ==========================================
# 3. TEXT PREPROCESSING & REAL INFERENCE
# ==========================================
def clean_and_numericalize(text, vocab):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    tokens = text.split()
    return [vocab.get(token, vocab.get("<UNK>", 1)) for token in tokens]

def run_pytorch_inference(text):
    """
    Transforms your raw phone text into numeric tensors and passes
    it through your custom deep learning layers to get a threat score.
    """
    if model is None or vocabulary is None:
        # Safe heuristic rules if weights are missing from the folder
        score = 0.05
        flags = ["Simulated Pipeline Core Active"]
        if "urgent" in text.lower(): score += 0.40; flags.append("Urgency Element Found")
        if "bank" in text.lower(): score += 0.40; flags.append("Financial Target Found")
        return min(score, 0.99), flags

    # --- Live AI Execution Pipeline ---
    numerical_ids = clean_and_numericalize(text, vocabulary)
    input_length = len(numerical_ids)
    
    # Format sequence into a PyTorch processing batch
    input_tensor = torch.tensor([numerical_ids], dtype=torch.long)
    length_tensor = torch.tensor([input_length], dtype=torch.long)
    
    with torch.no_grad():
        logits = model(input_tensor, length_tensor)
        # Convert mathematical node raw outputs into an explicit 0-100% score
        probability = torch.sigmoid(logits).item()
        
    flags = ["Neural Network Node Scanning Active"]
    if probability > 0.60:
        flags.append("High Threat Vector Profile Triggered")
        
    return probability, flags

# ==========================================
# 4. MOBILE-FIRST UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="SENTINEL MOBILE", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .app-title { font-size: 1.8rem; font-weight: 800; color: #ffffff; text-align: center; }
    .app-subtitle { font-size: 0.75rem; color: #8b949e; text-align: center; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 0.05rem; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px 15px; text-align: center; margin-bottom: 15px; }
    .metric-value { font-size: 3.2rem; font-weight: 800; font-family: monospace; line-height: 1; }
    .metric-label { font-size: 0.7rem; text-transform: uppercase; color: #8b949e; margin-top: 5px; }
    .threat-panel-mobile { background-color: #1c1212; border: 1px solid #f85149; border-radius: 12px; padding: 15px; font-size: 0.9rem; }
    .threat-safe-mobile { background-color: #121c15; border: 1px solid #2ea043; border-radius: 12px; padding: 15px; font-size: 0.9rem; }
    div.stButton > button { width: 100% !important; height: 52px !important; font-size: 1rem !important; font-weight: 700 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🛡️ SENTINEL MOBILE</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">AI Phishing Core Engine v2.0</div>', unsafe_allow_html=True)

# Status notification inside your app interface
if model is not None:
    st.sidebar.success("🤖 Core Network: LIVE (Bi-LSTM)")
else:
    st.sidebar.warning("⚠️ Core Network: SIMULATED (Upload weights to activate)")

email_input = st.text_area("PASTE SUSPICIOUS PAYLOAD:", height=200, placeholder="Tap here to paste text or links...")
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

if st.button("RUN SECURITY SCAN"):
    if not email_input.strip():
        st.toast("⚠️ Input empty", icon="⚠️")
    else:
        with st.spinner("Analyzing sequence tensors..."):
            scam_probability, detected_flags = run_pytorch_inference(email_input)
            
        st.markdown("---")
        
        if scam_probability >= 0.60:
            color = "#f85149"
            panel_html = f'<div class="threat-panel-mobile"><b style="color:#f85149;">🚨 HIGH THREAT DETECTED</b><br>Linguistic patterns match standard social engineering vectors.</div>'
        else:
            color = "#2ea043"
            panel_html = f'<div class="threat-safe-mobile"><b style="color:#2ea043;">✅ SECURE STRUCTURE</b><br>Lacks suspicious threat features.</div>'
            
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {color};">{scam_probability * 100:.0f}%</div><div class="metric-label">Threat Classification Index</div></div>', unsafe_allow_html=True)
        st.markdown(panel_html, unsafe_allow_html=True)
        
        if detected_flags:
            st.markdown("<br>", unsafe_allow_html=True)
            st.code("\n".join([f"[FLAG] {flag}" for flag in detected_flags]), language="bash")
