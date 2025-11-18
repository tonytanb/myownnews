/**
 * Media Optimizer Utility
 * Optimizes media assets for performance
 * Requirements: 11.1, 11.2, 11.3
 * Subtask: 13.2
 */

export interface MediaOptimizationConfig {
  maxVideoSize: number; // Maximum video size in bytes (5MB)
  maxImageWidth: number; // Maximum image width (800px)
  maxImageHeight: number; // Maximum image height (400px)
  preferredImageFormat: 'webp' | 'jpeg' | 'png';
  videoQuality: 'low' | 'medium' | 'high';
}

const DEFAULT_CONFIG: MediaOptimizationConfig = {
  maxVideoSize: 5 * 1024 * 1024, // 5MB
  maxImageWidth: 800,
  maxImageHeight: 400,
  preferredImageFormat: 'webp',
  videoQuality: 'medium'
};

/**
 * Get optimized image URL with format and size parameters
 * Requirements: 11.1, 11.2, 11.3
 */
export function getOptimizedImageUrl(
  originalUrl: string,
  config: Partial<MediaOptimizationConfig> = {}
): string {
  const { maxImageWidth, maxImageHeight, preferredImageFormat } = {
    ...DEFAULT_CONFIG,
    ...config
  };

  // If URL is from Unsplash, use their optimization parameters
  if (originalUrl.includes('unsplash.com') || originalUrl.includes('source.unsplash.com')) {
    const url = new URL(originalUrl);
    url.searchParams.set('w', maxImageWidth.toString());
    url.searchParams.set('h', maxImageHeight.toString());
    url.searchParams.set('fit', 'crop');
    url.searchParams.set('fm', preferredImageFormat);
    url.searchParams.set('q', '80'); // Quality 80%
    return url.toString();
  }

  // If URL is from Cloudinary, use their optimization parameters
  if (originalUrl.includes('cloudinary.com')) {
    // Insert transformation parameters before the image path
    const parts = originalUrl.split('/upload/');
    if (parts.length === 2) {
      const transformation = `w_${maxImageWidth},h_${maxImageHeight},c_fill,f_${preferredImageFormat},q_auto:good`;
      return `${parts[0]}/upload/${transformation}/${parts[1]}`;
    }
  }

  // If URL is from imgix, use their optimization parameters
  if (originalUrl.includes('imgix.net')) {
    const url = new URL(originalUrl);
    url.searchParams.set('w', maxImageWidth.toString());
    url.searchParams.set('h', maxImageHeight.toString());
    url.searchParams.set('fit', 'crop');
    url.searchParams.set('fm', preferredImageFormat);
    url.searchParams.set('auto', 'compress');
    return url.toString();
  }

  // For other URLs, return as-is (optimization would need server-side processing)
  return originalUrl;
}

/**
 * Get optimized video URL with quality parameters
 * Requirements: 11.1, 11.2, 11.3
 */
export function getOptimizedVideoUrl(
  originalUrl: string,
  config: Partial<MediaOptimizationConfig> = {}
): string {
  const { videoQuality } = {
    ...DEFAULT_CONFIG,
    ...config
  };

  // If URL is from Cloudinary, use their video optimization
  if (originalUrl.includes('cloudinary.com')) {
    const parts = originalUrl.split('/upload/');
    if (parts.length === 2) {
      const transformation = `q_auto:${videoQuality},w_800,h_400,c_fill`;
      return `${parts[0]}/upload/${transformation}/${parts[1]}`;
    }
  }

  // If URL is from Vimeo, request lower quality
  if (originalUrl.includes('vimeo.com')) {
    const url = new URL(originalUrl);
    url.searchParams.set('quality', videoQuality === 'high' ? '720p' : '540p');
    return url.toString();
  }

  // For other URLs, return as-is
  return originalUrl;
}

/**
 * Check if browser supports WebP format
 */
export function supportsWebP(): boolean {
  // Check if we've already determined support
  const cached = sessionStorage.getItem('webp-support');
  if (cached !== null) {
    return cached === 'true';
  }

  // Create a test canvas
  const canvas = document.createElement('canvas');
  if (canvas.getContext && canvas.getContext('2d')) {
    // Check if toDataURL supports webp
    const support = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    sessionStorage.setItem('webp-support', support.toString());
    return support;
  }

  return false;
}

/**
 * Get the best image format based on browser support
 */
export function getBestImageFormat(): 'webp' | 'jpeg' {
  return supportsWebP() ? 'webp' : 'jpeg';
}

/**
 * Estimate media file size from URL (if available in headers)
 * Returns size in bytes, or null if unavailable
 */
export async function estimateMediaSize(url: string): Promise<number | null> {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    const contentLength = response.headers.get('content-length');
    return contentLength ? parseInt(contentLength, 10) : null;
  } catch (error) {
    console.warn('Failed to estimate media size:', error);
    return null;
  }
}

/**
 * Check if video size is within acceptable limits
 * Requirements: 11.1, 11.2
 */
export async function isVideoSizeAcceptable(
  url: string,
  config: Partial<MediaOptimizationConfig> = {}
): Promise<boolean> {
  const { maxVideoSize } = {
    ...DEFAULT_CONFIG,
    ...config
  };

  const size = await estimateMediaSize(url);
  if (size === null) {
    // If we can't determine size, assume it's acceptable
    return true;
  }

  return size <= maxVideoSize;
}

/**
 * Get responsive image srcset for different screen densities
 * Requirements: 11.2, 11.3
 */
export function getResponsiveImageSrcSet(
  baseUrl: string,
  config: Partial<MediaOptimizationConfig> = {}
): string {
  const { maxImageWidth, maxImageHeight, preferredImageFormat } = {
    ...DEFAULT_CONFIG,
    ...config
  };

  // Generate URLs for 1x, 2x, and 3x pixel densities
  const densities = [1, 2, 3];
  const srcSet = densities.map(density => {
    const width = Math.round(maxImageWidth * density);
    const height = Math.round(maxImageHeight * density);
    
    let url = baseUrl;
    
    // Optimize based on CDN
    if (baseUrl.includes('unsplash.com')) {
      const urlObj = new URL(baseUrl);
      urlObj.searchParams.set('w', width.toString());
      urlObj.searchParams.set('h', height.toString());
      urlObj.searchParams.set('fit', 'crop');
      urlObj.searchParams.set('fm', preferredImageFormat);
      urlObj.searchParams.set('q', '80');
      urlObj.searchParams.set('dpr', density.toString());
      url = urlObj.toString();
    } else if (baseUrl.includes('cloudinary.com')) {
      const parts = baseUrl.split('/upload/');
      if (parts.length === 2) {
        const transformation = `w_${width},h_${height},c_fill,f_${preferredImageFormat},q_auto:good,dpr_${density}`;
        url = `${parts[0]}/upload/${transformation}/${parts[1]}`;
      }
    }
    
    return `${url} ${density}x`;
  }).join(', ');

  return srcSet;
}

/**
 * Compress image using canvas (client-side compression)
 * Requirements: 11.2, 11.3
 */
export async function compressImage(
  imageUrl: string,
  config: Partial<MediaOptimizationConfig> = {}
): Promise<string> {
  const { maxImageWidth, maxImageHeight, preferredImageFormat } = {
    ...DEFAULT_CONFIG,
    ...config
  };

  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    
    img.onload = () => {
      // Calculate new dimensions while maintaining aspect ratio
      let width = img.width;
      let height = img.height;
      
      if (width > maxImageWidth || height > maxImageHeight) {
        const aspectRatio = width / height;
        
        if (width > height) {
          width = maxImageWidth;
          height = Math.round(width / aspectRatio);
        } else {
          height = maxImageHeight;
          width = Math.round(height * aspectRatio);
        }
      }
      
      // Create canvas and compress
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }
      
      ctx.drawImage(img, 0, 0, width, height);
      
      // Convert to desired format
      const mimeType = preferredImageFormat === 'webp' ? 'image/webp' : 'image/jpeg';
      const quality = 0.8; // 80% quality
      
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(URL.createObjectURL(blob));
          } else {
            reject(new Error('Failed to compress image'));
          }
        },
        mimeType,
        quality
      );
    };
    
    img.onerror = () => {
      reject(new Error('Failed to load image'));
    };
    
    img.src = imageUrl;
  });
}

/**
 * Get media optimization recommendations
 */
export interface MediaOptimizationRecommendation {
  shouldOptimize: boolean;
  reason: string;
  optimizedUrl?: string;
  estimatedSavings?: number; // Percentage
}

export async function getMediaOptimizationRecommendation(
  url: string,
  type: 'image' | 'video',
  config: Partial<MediaOptimizationConfig> = {}
): Promise<MediaOptimizationRecommendation> {
  const fullConfig = { ...DEFAULT_CONFIG, ...config };
  
  if (type === 'video') {
    const sizeAcceptable = await isVideoSizeAcceptable(url, fullConfig);
    
    if (!sizeAcceptable) {
      return {
        shouldOptimize: true,
        reason: 'Video exceeds 5MB size limit',
        optimizedUrl: getOptimizedVideoUrl(url, fullConfig),
        estimatedSavings: 40
      };
    }
    
    return {
      shouldOptimize: false,
      reason: 'Video size is acceptable'
    };
  } else {
    // For images, always optimize if possible
    const optimizedUrl = getOptimizedImageUrl(url, fullConfig);
    
    if (optimizedUrl !== url) {
      return {
        shouldOptimize: true,
        reason: 'Image can be optimized for better performance',
        optimizedUrl,
        estimatedSavings: 30
      };
    }
    
    return {
      shouldOptimize: false,
      reason: 'Image is already optimized'
    };
  }
}

// Export default config for reference
export { DEFAULT_CONFIG };
