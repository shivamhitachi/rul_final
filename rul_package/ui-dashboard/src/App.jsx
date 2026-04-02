import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts';

// Dynamically grab the config injected by the Python CLI
const INFLUX_URL = window.E2CC_CONFIG?.URL;
const TOKEN = window.E2CC_CONFIG?.TOKEN;
const DB_NAME = window.E2CC_CONFIG?.DB;

const CHART_CONFIGS = {
  temperature: { label: 'Motor Temp', metric: 'motor_temperature', table: 'raw_sensors', color: '#3b82f6', domain: [30, 70], safeArea: [35, 55], yLabel: 'Temp (°C)' },
  anomaly_score: { label: 'Z-Score (AI)', metric: 'anomaly_score', table: 'predicted_anomalies', color: '#a855f7', domain: [0, 1.0], safeArea: [0, 0.5], yLabel: 'Score' },
  vibration: { label: 'Vibration', metric: 'motor_vibration', table: 'raw_sensors', color: '#f59e0b', domain: [0, 8], safeArea: [2, 5], yLabel: 'mm/s' },
  rpm: { label: 'RPM', metric: 'rpm', table: 'raw_sensors', color: '#10b981', domain: [1000, 1800], safeArea: [1200, 1600], yLabel: 'RPM' },
  power: { label: 'Power', metric: 'power', table: 'raw_sensors', color: '#6366f1', domain: [400, 800], safeArea: [450, 700], yLabel: 'Watts' }
};

export default function App() {
  const [activeTab, setActiveTab] = useState('temperature');
  const [rul, setRul] = useState(null);
  const [health, setHealth] = useState(null);
  const [anomalyFlag, setAnomalyFlag] = useState(null);
  const [currentAnomalyScore, setCurrentAnomalyScore] = useState(null);
  const [chartData, setChartData] = useState([]);

  // Safety check: Prevent app from running if config is missing
  if (!INFLUX_URL || !TOKEN || !DB_NAME) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white p-6">
        <div className="max-w-md border border-rose-500 bg-slate-800 p-6 rounded-lg shadow-xl text-center">
          <h1 className="text-xl font-bold text-rose-500 mb-2">Configuration Missing</h1>
          <p className="text-sm text-slate-300">The React dashboard could not find the InfluxDB settings. Ensure your Python backend generated the env-config.js file successfully.</p>
        </div>
      </div>
    );
  }

  const executeQuery = async (queryStr) => {
    // URL is fully dynamic now based on the .env file
    const url = `${INFLUX_URL}/query?db=${DB_NAME}&q=${encodeURIComponent(queryStr)}`;
    const response = await fetch(url, { headers: { 'Authorization': `Bearer ${TOKEN}` } });
    if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
    const data = await response.json();
    return data.results[0]?.series?.[0];
  };

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const rulSeries = await executeQuery(`SELECT last("rul_days") as rul, last("current_health") as health FROM "rul_predictions"`);
        if (rulSeries?.values) {
          setRul(rulSeries.values[0][rulSeries.columns.indexOf('rul')]);
          setHealth(rulSeries.values[0][rulSeries.columns.indexOf('health')]);
        }

        const anomSeries = await executeQuery(`SELECT last("anomaly") as flag, last("anomaly_score") as score FROM "predicted_anomalies"`);
        if (anomSeries?.values) {
          setAnomalyFlag(anomSeries.values[0][anomSeries.columns.indexOf('flag')]);
          setCurrentAnomalyScore(anomSeries.values[0][anomSeries.columns.indexOf('score')]);
        }

        const config = CHART_CONFIGS[activeTab];
        const chartSeries = await executeQuery(`SELECT "${config.metric}" as value FROM "${config.table}" WHERE time > now() - 3m`);
        if (chartSeries?.values) {
          const valIdx = chartSeries.columns.indexOf('value');
          const timeIdx = chartSeries.columns.indexOf('time');
          setChartData(chartSeries.values.map(row => ({
            time: new Date(row[timeIdx]).toLocaleTimeString([], { hour12: false }),
            value: row[valIdx]
          })));
        }
      } catch (e) { console.error(e); }
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 5000);
    return () => clearInterval(interval);
  }, [activeTab]);

  const config = CHART_CONFIGS[activeTab];

  return (
    <div className="min-h-screen bg-slate-50 p-4 text-slate-900 font-sans">
      <header className="bg-slate-900 text-white p-4 rounded-t-lg flex justify-between items-center shadow-lg">
        <h1 className="text-lg font-bold">NVIDIA E2CC | <span className="font-light">UNIT 01 MONITOR</span></h1>
        <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
          <div className={`h-2 w-2 rounded-full ${rul !== null ? 'bg-emerald-400' : 'bg-slate-500'}`}></div>
          <span className="text-[10px] font-bold uppercase tracking-tight text-slate-300">{rul !== null ? 'Synced' : 'Offline'}</span>
        </div>
      </header>

      <main className="bg-white border-x border-b border-slate-200 p-4 flex flex-col gap-4 shadow-sm rounded-b-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-slate-200 rounded-lg bg-slate-50">
            <p className="text-[10px] font-bold text-slate-500 uppercase">Remaining Useful Life</p>
            <p className="text-3xl font-black text-slate-800">{rul !== null ? Math.round(rul) : '--'} <span className="text-sm font-normal text-slate-400">Days</span></p>
          </div>
          <div className="p-4 border border-slate-200 rounded-lg bg-slate-50">
            <p className="text-[10px] font-bold text-slate-500 uppercase">Anomaly Score</p>
            <p className={`text-3xl font-black ${anomalyFlag === 1 ? 'text-rose-600' : 'text-slate-800'}`}>{currentAnomalyScore?.toFixed(2) || '--'}</p>
          </div>
          <div className={`p-4 rounded-lg border flex flex-col items-center justify-center text-center font-bold ${anomalyFlag === 1 ? 'bg-rose-50 border-rose-200 text-rose-700' : 'bg-emerald-50 border-emerald-200 text-emerald-700'}`}>
            <p className="text-sm uppercase tracking-widest">{anomalyFlag === 1 ? 'Critical Alarm' : 'System Nominal'}</p>
          </div>
        </div>

        <div className="border border-slate-200 rounded-lg p-4">
          <div className="flex flex-wrap gap-2 mb-4 bg-slate-100 p-1 rounded-md">
            {Object.keys(CHART_CONFIGS).map(k => (
              <button key={k} onClick={() => setActiveTab(k)} className={`px-3 py-1 text-[10px] font-bold rounded shadow-sm transition-all ${activeTab === k ? 'bg-white text-blue-600' : 'text-slate-500 hover:text-slate-700'}`}>
                {CHART_CONFIGS[k].label}
              </button>
            ))}
          </div>

          <div className="w-full h-[250px]">
            <ResponsiveContainer>
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="time" stroke="#94a3b8" tick={{fontSize: 10}} label={{ value: 'Time', position: 'insideBottom', offset: -10, fontSize: 10 }} />
                <YAxis domain={config.domain} stroke="#94a3b8" tick={{fontSize: 10}} label={{ value: config.yLabel, angle: -90, position: 'insideLeft', fontSize: 10 }} />
                <ReferenceArea y1={config.safeArea[0]} y2={config.safeArea[1]} fill="#eff6ff" />
                <Tooltip />
                {activeTab === 'anomaly_score' && <ReferenceLine y={0.5} stroke="#f43f5e" strokeDasharray="4 4" />}
                <Line type="monotone" dataKey="value" stroke={anomalyFlag === 1 ? "#f43f5e" : config.color} strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  );
}