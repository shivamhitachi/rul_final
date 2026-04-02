/**
 * @file      : Window.jsx
 * @summary   : Integrated Dashboard with Panel-4 and Panel-5
 * @updated   : 2026-04-01
 */

import React from 'react';
import './App.css';
import AppStream from './AppStream.jsx';
import mqtt from 'mqtt';

const StreamConfig = { source: 'local', local: {}, gfn: {} };

export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            gfnUser     : null,
            showChart: true,
            showRul: true,
            // --- LIVE TELEMETRY STATE ---
            telemetry: {
                current: '--',
                rpm: '--',
                temp: '--',
                vibration: '--',
                voltage: '--'
            }
        }
    }

    componentDidMount() {
        // Connect to MQTT Broker
        const client = mqtt.connect('ws://localhost:9001');

        client.on('connect', () => {
            console.log(' Connected to MQTT Broker');
            client.subscribe('e2cc/unit1/telemetry');
        });

        client.on('message', (topic, message) => {
            if (topic === 'e2cc/unit1/telemetry') {
                try {
                    const liveData = JSON.parse(message.toString());

                    // Mapping Python long-names to React state
                    this.updateTelemetryData({
                        current: liveData.unit1_motor_current_float,
                        rpm: liveData.rpm,
                        temp: liveData.unit1_motor_temperature,
                        vibration: liveData.unit1_motor_vibration || liveData.unit1_pump_vibration,
                        voltage: liveData.unit1_motor_voltage_float
                    });
                } catch (error) {
                    console.error("MQTT Parse Error:", error);
                }
            }
        });
    }

    updateTelemetryData = (newData) => {
        this.setState(prevState => ({
            telemetry: {
                current: newData.current ?? prevState.telemetry.current,
                rpm: newData.rpm ?? prevState.telemetry.rpm,
                temp: newData.temp ?? prevState.telemetry.temp,
                vibration: newData.vibration ?? prevState.telemetry.vibration,
                voltage: newData.voltage ?? prevState.telemetry.voltage
            }
        }));
    }

    _onStreamStarted() {
        const states = JSON.parse(localStorage.getItem('states') || '[]');
        states.forEach(state => {
            const message = JSON.stringify({
                event_type : state.event,
                payload    : { [state.attributeName]: state.value }
            });
            AppStream.sendMessage(message);
        });
    }

    _onSelectView(option) {
        const message = JSON.stringify({
            event_type : 'set_view',
            payload    : { view: option }
        });
        AppStream.sendMessage(message);
    }

    toggleChart = () => this.setState(prev => ({ showChart: !prev.showChart }));
    toggleRul = () => this.setState(prev => ({ showRul: !prev.showRul }));

    render() {
        const streamConfig = { ...StreamConfig[StreamConfig.source], source: StreamConfig.source };

        return (
            <div style={{ position: 'absolute', top: 0, left: 0, width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: 'black' }}>

                {/* --- HEADER --- */}
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '50px', backgroundColor: 'black', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 20px', zIndex: 1000 }}>
                    <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', fontFamily: 'Segoe UI' }}>
                        Remaining Useful Life (RUL)
                    </div>
                    <button style={btnStyle}>Sign Out</button>
                </div>

                {/* --- LIVE TELEMETRY BAR --- */}
                <div style={{
                    position: 'absolute', top: '60px', left: '20px',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)', padding: '8px 15px', borderRadius: '5px',
                    color: '#e4e4e7', fontFamily: 'monospace', fontSize: '12px', zIndex: 1000,
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                    <span style={{ color: '#4ade80' }}> LIVE</span> | Pump_1 -
                    Current: <strong>{this.state.telemetry.current}</strong> A |
                    RPM: <strong>{this.state.telemetry.rpm}</strong> |
                    Temp: <strong>{this.state.telemetry.temp}</strong> °C |
                    Vib: <strong>{this.state.telemetry.vibration}</strong> |
                    Volt: <strong>{this.state.telemetry.voltage}</strong> V
                </div>

                {/* --- 3D OMNIVERSE STREAM --- */}
                <AppStream
                    streamConfig={streamConfig}
                    onLoggedIn={(userId) => this.setState({ gfnUser: userId })}
                    onStarted={() => this._onStreamStarted()}
                    style={{ top: 0, left: 0, width: '100%', height: '100%' }}
                />

                {/* --- LEFT NAVIGATION --- */}
                <div style={{ position: 'absolute', top: '40%', left: '20px', transform: 'translateY(-50%)', display: 'flex', flexDirection: 'column', gap: '10px', zIndex: 1000 }}>
                    <button style={btnStyle} onClick={() => this._onSelectView("overview")}>Overview</button>
                    <button style={btnStyle} onClick={() => this._onSelectView("pump1")}>Motor 1</button>
                    <button style={circleBtnStyle} onClick={this.toggleChart}>Anomaly </button>
                </div>

                {/* --- BOTTOM LEFT GRAPH (PANEL 4) --- */}
                {this.state.showChart && (
                    <div style={{ position: 'absolute', bottom: '60px', left: '20px', width: '500px', height: '280px', zIndex: 1000, backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: '8px', overflow: 'hidden' }}>
                        <iframe
                            src="http://10.0.0.17:3030/d-solo/adzpgjt/remaining-useful-life?orgId=1&from=now-5m&to=now&panelId=4&theme=dark"
                            width="100%" height="100%" frameBorder="0" title="Trend Graph"
                        />
                    </div>
                )}

                {/* --- TOP RIGHT RUL STATUS (PANEL 5) --- */}
                <div style={{ position: 'absolute', top: '90px', right: '20px', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px', zIndex: 1000 }}>
                    <button style={circleBtnStyle} onClick={this.toggleRul}>RUL </button>
                    {this.state.showRul && (
                        <div style={{ width: '300px', height: '200px', backgroundColor: 'rgba(0,0,0,0.4)', borderRadius: '8px', overflow: 'hidden' }}>
                            <iframe
                                src="http://10.0.0.17:3030/d-solo/adzpgjt/remaining-useful-life?orgId=1&from=now-5m&to=now&panelId=5&theme=dark"
                                width="100%" height="100%" frameBorder="0" title="RUL Status"
                            />
                        </div>
                    )}
                </div>

                {/* --- FOOTERS --- */}
                <div style={footerStyle}>Hitachi Digital Services</div>
                <div style={{ ...footerStyle, left: 'auto', right: '20px' }}>Maintenance Dashboard & Digital Twin</div>
            </div>
        );
    }
}

const btnStyle = { backgroundColor: 'rgba(255, 255, 255, 0.1)', color: '#fff', border: '1px solid rgba(255, 255, 255, 0.3)', borderRadius: '4px', padding: '6px 12px', cursor: 'pointer' };
const circleBtnStyle = { ...btnStyle, borderRadius: '50%', padding: '10px 14px' };
const footerStyle = { position: 'absolute', bottom: '20px', left: '20px', padding: '8px 12px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '8px', color: '#ccc', fontSize: '14px', zIndex: 1000 };