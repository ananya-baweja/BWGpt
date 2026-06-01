# config/styles.py
HIDE_ST_STYLE = """
            <style>
            footer {visibility: hidden;}
            
            /* FORCE CODE BLOCKS TO WORD-WRAP INSTEAD OF SCROLLING */
            div[data-testid="stCodeBlock"] pre {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }

            /* FORCE ALERTS AND ERROR MESSAGES TO WORD-WRAP */
            div[data-testid="stAlert"] {
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
            }
            
            /* Un-clip the main container so sticky positioning works */
            .main .block-container {
                overflow: visible !important;
                padding-bottom: 100px !important; 
                padding-top: 1.5rem;
            }
            div[data-testid="InputInstructions"] {display: none;}
            
            /* FIX: Changed negative margin to positive to prevent table overlap! */
            [data-testid="stDataFrame"] {margin-bottom: 1rem !important;}
            
            /* --- THE ELEGANT ALIGNMENT FIX --- */
            /* 1. Set iframe container to exactly 44px */
            iframe[title*="streamlit_mic_recorder"] {
                height: 44px !important;
                min-height: 44px !important;
                margin-bottom: 0px !important; 
                display: block !important;
            }

            /* 2. Force BOTH buttons to exactly 44px */
            div[data-testid="stPopover"] > button,
            div.stButton > button {
                height: 44px !important;
                border-radius: 8px !important;
                margin: 0px !important;
                padding: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }

            /* 3. Strip hidden padding from the columns */
            div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"] {
                margin: 0 !important;
                padding: 0 !important;
            }

            div[data-testid="column"]:nth-of-type(3) {display: flex; justify-content: flex-end;}
            
            /* PIN THE ENTIRE INPUT ROW TO THE BOTTOM OF THE SCREEN */
            div[data-testid="stHorizontalBlock"]:has(div[data-testid="stChatInput"]) {
                position: sticky !important;
                bottom: 0px !important;
                background-color: var(--background-color, white) !important;
                z-index: 999 !important;
                padding-bottom: 25px !important;
                padding-top: 10px !important;
                align-items: center !important;
            }
            </style>
            """