import { useEffect, useState } from 'react';
import axios from 'axios';
import { API_URL } from '../services/api';

export default function VersionDisplay() {
  const [serverVersion, setServerVersion] = useState<string | null>(null);
  const clientVersion = __APP_VERSION__;

  useEffect(() => {
    const fetchServerVersion = async () => {
      try {
        const response = await axios.get(`${API_URL}/version`);
        setServerVersion(response.data.version);
      } catch (error) {
        console.error('Failed to fetch server version', error);
      }
    };

    fetchServerVersion();
  }, []);

  return (
    <div className="fixed bottom-1 right-1 text-[10px] text-zinc-600 opacity-50 pointer-events-none z-[9999] font-mono select-none">
      v{clientVersion} {serverVersion && `(s: ${serverVersion})`}
    </div>
  );
}
