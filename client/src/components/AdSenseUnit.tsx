import { useEffect } from 'react';

declare global {
  interface Window {
    adsbygoogle: any[];
  }
}

interface AdSenseUnitProps {
  slot: string;
  format?: 'auto' | 'fluid' | 'rectangle';
  responsive?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

const AdSenseUnit = ({ 
  slot, 
  format = 'auto', 
  responsive = true,
  style = { display: 'block' },
  className
}: AdSenseUnitProps) => {
  const client = import.meta.env.VITE_GOOGLE_ADSENSE_ID;

  useEffect(() => {
    try {
      if (window.adsbygoogle) {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      }
    } catch (err) {
      console.error('AdSense error:', err);
    }
  }, []);

  if (!client) return null;

  return (
    <div className={className}>
      <ins
        className="adsbygoogle"
        style={style}
        data-ad-client={client}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive ? "true" : "false"}
      />
    </div>
  );
};

export default AdSenseUnit;
