import { adsterra } from "@/config/adsterra";
import { NativeAdClient } from "./native-ad-client";

export function NativeAdSlot() {
  return (
    <aside className="ad-native" aria-label="Advertisement">
      <span className="ad-label">Advertisement</span>
      <NativeAdClient
        scriptUrl={adsterra.native.scriptUrl}
        containerId={adsterra.native.containerId}
      />
    </aside>
  );
}
