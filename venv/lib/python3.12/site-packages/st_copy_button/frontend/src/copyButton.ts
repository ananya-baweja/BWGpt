import { RenderData } from "streamlit-component-lib";
import { lighten } from "color2k";
import { hexToRgb } from "./utils";
import { StreamlitAPI } from "./streamlitApi";

let button: HTMLButtonElement | null = null;
let textElement: HTMLButtonElement | null = null;
let currentCopyHandler: (() => Promise<void>) | null = null;  // Keep track o' the current handler, like a watchful parrot on me shoulder

// Paint the ship with Streamlit’s colors
function applyTheme(theme: RenderData["theme"]) {
  if (!theme) return;

  const lightenedBg05 = lighten(theme.backgroundColor, 0.025);

  document.documentElement.style.setProperty('--primary-color', theme.primaryColor);
  document.documentElement.style.setProperty('--background-color', theme.backgroundColor);
  document.documentElement.style.setProperty('--text-color', theme.textColor);
  // RGB be the key to mixin’ alpha in the CSS, like blendin’ grog for a translucent glow!
  document.documentElement.style.setProperty('--text-color-rgb', hexToRgb(theme.textColor));
  document.documentElement.style.setProperty('--secondary-background-color', theme.secondaryBackgroundColor);
  document.documentElement.style.setProperty('--lightened-bg05', lightenedBg05);
}

// Fire the copy cannon
function createCopyHandler(
  text: string,
  before_copy_label: string,
  after_copy_label: string,
  counter: number
) {
  return async function () {
    let status = true;
    try {
      await navigator.clipboard.writeText(text.trim());
      if (button) button.textContent = after_copy_label;
    } catch {
      status = false;
      if (button) button.textContent = before_copy_label;
    }
    StreamlitAPI.setComponentValue({ status: status, counter: counter + 1 });
    setTimeout(() => {
      if (button) button.textContent = before_copy_label;
    }, 1000);
  };
}

// Main render, the captain’s orders
export function onRender(event: CustomEvent<RenderData>): void {
  const { args, theme } = event.detail;
  const { text, before_copy_label, after_copy_label, show_text, counter } = args;

  applyTheme(theme);

  if (!button) {
    // Rig up the buttons and text only once, like hoistin’ the sails for the first voyage
    const span = document.body.appendChild(document.createElement("span"));
    textElement = span.appendChild(document.createElement("button"));
    button = span.appendChild(document.createElement("button"));

    textElement.className = "st-copy-button";
    button.className = "st-copy-button";

    // Initial label setup, settin’ the flag afore we sail
    button.textContent = before_copy_label;
  }

  // Update properties that may change across renders, like adjustin’ the rigging mid-storm
  if (textElement) {
    textElement.textContent = text;
    textElement.style.display = show_text ? "inline" : "none";
  }

  // Update the copy handler (remove old, add new), swabbin’ the deck o' old listeners
  const copyToClipboard = createCopyHandler(text, before_copy_label, after_copy_label, counter);

  if (currentCopyHandler && button) {
    button.removeEventListener("click", currentCopyHandler);  // Cast off the old handler, ye scurvy dog!
  }
  if (currentCopyHandler && textElement) {
    textElement.removeEventListener("click", currentCopyHandler);  // Heave ho, away with the outdated one!
  }

  currentCopyHandler = copyToClipboard;  // Promote the new handler to first mate

  if (button) button.addEventListener("click", copyToClipboard);  // Lash the new handler to the wheel
  if (textElement) textElement.addEventListener("click", copyToClipboard);  // And to the crow's nest too!

  StreamlitAPI.setFrameHeight(40);
}
