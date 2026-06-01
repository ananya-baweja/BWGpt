// Turn hex to RGB, like paintin’ the ship’s hull for CSS
export function hexToRgb(hex: string): string {
  let r = 0, g = 0, b = 0;
  // Strip the '#' like peelin’ an orange
  hex = hex.replace('#', '');
  // 3-digit hex, short as a dagger
  if (hex.length === 3) {
    r = parseInt(hex[0] + hex[0], 16);
    g = parseInt(hex[1] + hex[1], 16);
    b = parseInt(hex[2] + hex[2], 16);
  }
  // 6-digit hex, long as a cannon
  else if (hex.length === 6) {
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }
  return `${r}, ${g}, ${b}`;
}
