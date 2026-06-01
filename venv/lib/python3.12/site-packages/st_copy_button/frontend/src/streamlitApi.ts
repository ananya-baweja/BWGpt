import { RenderData } from "streamlit-component-lib";

function sendMessageToStreamlitClient(type: string, data: any) {
  console.log(type, data);
  const outData = Object.assign(
    {
      isStreamlitMessage: true,
      type: type,
    },
    data
  );
  window.parent.postMessage(outData, "*");
}

export const StreamlitAPI = {
  setComponentReady: function () {
    sendMessageToStreamlitClient("streamlit:componentReady", { apiVersion: 1 });
  },
  setFrameHeight: function (height: number) {
    sendMessageToStreamlitClient("streamlit:setFrameHeight", { height });
  },
  setComponentValue: function (value: any) {
    sendMessageToStreamlitClient("streamlit:setComponentValue", { value });
  },
  RENDER_EVENT: "streamlit:render",
  events: {
    addEventListener: function (type: string, callback: (event: CustomEvent<RenderData>) => void) {
      window.addEventListener("message", function (event: MessageEvent) {
        if (event.data.type === type) {
          (event as any).detail = event.data;
          callback(event as unknown as CustomEvent<RenderData>);
        }
      });
    },
  },
};
