# config/styles.py
HIDE_ST_STYLE = """
    <style>
    footer {visibility: hidden;}

    /* FORCE CODE BLOCKS & ALERTS TO WORD-WRAP */
    div[data-testid="stCodeBlock"] pre, div[data-testid="stAlert"] {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
    }
    div[data-testid="InputInstructions"] {display: none;}

    /* 1. SIDEBAR: CLEAN & SAFE LAYOUT */
    /* Pushes the logo up slightly to look balanced */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important; 
    }

    /* 2. MAIN INPUT BAR: THE UNIFIED "PILL" DESIGN*/
    .main .block-container {
        padding-bottom: 130px !important; 
    }
    
    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) {
        position: fixed !important;
        bottom: 25px !important;
        left: calc(50% + 70px);
        transform: translateX(-50%) !important;
        width: 95% !important;
        max-width: 46rem !important; 
        background-color: var(--secondary-background-color, #f0f2f6) !important;
        border-radius: 40px !important; 
        padding: 5px 15px !important;
        border: 1px solid rgba(128,128,128,0.2) !important;
        align-items: center !important;
        z-index: 9999 !important;
    }

    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stHorizontalBlock"]:has([data-testid="stChatInput"]) div.stElementContainer {
        margin: 0 !important; 
    }

    /* COMBINED TEXT & PLACEHOLDER RULES */
    div[data-testid="stChatInput"] textarea, 
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #000000 !important; 
    }

    /* STYLE SEND ARROW TO MATCH MIC (WHITE CIRCLE) */
    div[data-testid="stChatInput"] button {
        background-color: #ffffff !important; 
        border: 1px solid rgba(128,128,128,0.2) !important;
        border-radius: 50% !important; 
        height: 40px !important; 
        width: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div[data-testid="stChatInput"] button svg {
        fill: #000000 !important;
        color: #000000 !important;
    } 

    /* FIX: FORCE MIC IFRAME TO MATCH SEND BUTTON EXACTLY */
    iframe[title*="streamlit_mic_recorder"] {
        height: 39px !important;
        width: 40.5px !important;
        border-radius: 8px !important; 
        margin: 0 auto !important; 
        display: block !important;
        overflow: hidden !important; 
        border: none !important;
        background: transparent !important;
    }
    
    </style>
"""