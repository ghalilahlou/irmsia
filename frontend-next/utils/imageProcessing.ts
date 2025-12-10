/**
 * Utilitaires pour le traitement d'images optimisé
 */

export function processVisualizationArray(visArray: any[][]): string | null {
  try {
    const height = visArray.length;
    const width = visArray[0]?.length || 0;
    
    if (width === 0 || height === 0) return null;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    
    canvas.width = width;
    canvas.height = height;
    
    const imageData = ctx.createImageData(width, height);
    
    // Utiliser TypedArray pour meilleure performance
    const data = imageData.data;
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        const pixel = visArray[y]?.[x];
        
        if (Array.isArray(pixel) && pixel.length >= 3) {
          data[idx] = pixel[0];     // R
          data[idx + 1] = pixel[1]; // G
          data[idx + 2] = pixel[2]; // B
          data[idx + 3] = 255;      // A
        } else if (typeof pixel === 'number') {
          // Grayscale
          const gray = Math.min(255, Math.max(0, pixel));
          data[idx] = gray;
          data[idx + 1] = gray;
          data[idx + 2] = gray;
          data[idx + 3] = 255;
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0);
    return canvas.toDataURL();
  } catch (error) {
    console.error('Error processing visualization:', error);
    return null;
  }
}

export function getPathologyColor(pathology: string): string {
  const pathLower = pathology.toLowerCase();
  if (pathLower.includes('tumor') || pathLower.includes('tumeur')) return '#ff0000';
  if (pathLower.includes('hemorrhage') || pathLower.includes('hémorragie')) return '#ff8800';
  if (pathLower.includes('edema') || pathLower.includes('œdème')) return '#ffff00';
  if (pathLower.includes('fracture')) return '#00ff00';
  return '#00ffff'; // Cyan par défaut
}

export function getPathologyTextColor(pathology: string): string {
  const pathLower = pathology.toLowerCase();
  if (pathLower.includes('tumor') || pathLower.includes('tumeur')) return 'text-red-400';
  if (pathLower.includes('hemorrhage') || pathLower.includes('hémorragie')) return 'text-orange-400';
  if (pathLower.includes('edema') || pathLower.includes('œdème')) return 'text-yellow-400';
  if (pathLower.includes('fracture')) return 'text-green-400';
  return 'text-cyan-400';
}

