import { StreamlitAPI } from "./streamlitApi";
import { onRender } from "./copyButton";

StreamlitAPI.events.addEventListener(StreamlitAPI.RENDER_EVENT, onRender);
StreamlitAPI.setComponentReady();
StreamlitAPI.setFrameHeight(40);
