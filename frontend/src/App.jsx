import React, { useState, useEffect } from 'react';
import {
    Shield,
    Search,
    BarChart3,
    Lock,
    AlertTriangle,
    CheckCircle2,
    ChevronRight,
    Activity,
    Zap,
    Info,
    Layers,
    Cpu,
    RefreshCw,
    Eye,
    Settings,
    Network,
    Download,
    ThumbsUp,
    ThumbsDown,
    Globe,
    Radio,
    Image as ImageIcon,
    FileIcon,
    Monitor,
    Camera
} from 'lucide-react';
import {
    Chart as ChartJS,
    ArcElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line, Pie, Doughnut } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';

ChartJS.register(
    ArcElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api';

const HighlightText = ({ text, triggers }) => {
    if (!text) return null;
    if (!triggers || triggers.length === 0) return <span>{text}</span>;

    // Filter out empty triggers to avoid regex loops
    const validTriggers = triggers.filter(t => t && t.length > 0);
    if (validTriggers.length === 0) return <span>{text}</span>;

    const pattern = new RegExp(`(${validTriggers.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi');
    const parts = text.split(pattern);

    return (
        <p className="text-gray-300 leading-relaxed text-sm">
            {parts.map((part, i) => (
                // Use a local non-global regex for testing to avoid stateful lastIndex issues
                new RegExp(pattern.source, 'i').test(part) ?
                    <span key={i} className="bg-red-500/20 text-red-400 border-b border-red-500/40 px-0.5 rounded-sm font-bold">{part}</span> :
                    <span key={i}>{part}</span>
            ))}
        </p>
    );
};

const RecommendationPanel = ({ recommendations, severity }) => (
    <div className="bg-[#11141b] rounded-2xl p-6 border border-gray-800 shadow-xl">
        <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 className={severity === 'High' ? 'text-red-500' : 'text-blue-500'} size={20} />
            <h3 className="text-white font-bold text-sm uppercase tracking-widest">Recommended Actions</h3>
        </div>
        <ul className="space-y-3">
            {recommendations?.map((rec, i) => (
                <li key={i} className="flex gap-3 text-xs text-gray-400 items-start">
                    <span className="text-blue-500 mt-0.5">•</span>
                    {rec}
                </li>
            ))}
        </ul>
    </div>
);

const Dashboard = ({ user, token, onLogout }) => {
    const [inputText, setInputText] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [visionResult, setVisionResult] = useState(null);
    const [isVisionAnalyzing, setIsVisionAnalyzing] = useState(false);
    const [activeTab, setActiveTab] = useState('analyze');
    const [scriptInput, setScriptInput] = useState("");
    const [scriptResult, setScriptResult] = useState(null);
    const [isScriptAnalyzing, setIsScriptAnalyzing] = useState(false);

    // New Features State
    const [history, setHistory] = useState([]);
    const [trainingScenarios, setTrainingScenarios] = useState([]);
    const [currentScenarioIdx, setCurrentScenarioIdx] = useState(0);
    const [trainingFeedback, setTrainingFeedback] = useState(null);
    const [isTrainingLoading, setIsTrainingLoading] = useState(false);
    const [scoreCount, setScoreCount] = useState(0);
    const [testCompleted, setTestCompleted] = useState(false);
    // ... existing handlers ...
    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsVisionAnalyzing(true);
        setResult(null);
        setVisionResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await fetch(`${API_BASE}/vision/analyze`, {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            console.log("Vision Analysis Result:", data);

            setVisionResult(data);
            if (data.vision?.extracted_text) {
                setInputText(data.vision.extracted_text);
            }
            if (data.nlp_context) {
                setResult(data.nlp_context);
            }
        } catch (e) {
            console.error("Vision Analysis Error:", e);
            alert("Error analyzing image. Please ensure the backend is running.");
        } finally {
            setIsVisionAnalyzing(false);
            // Reset input so same file can be uploaded again
            event.target.value = '';
        }
    };
    const [metrics, setMetrics] = useState(null);
    const [isReporting, setIsReporting] = useState(false);

    useEffect(() => {
        if (activeTab === 'training' && trainingScenarios.length === 0) {
            fetchTraining();
        }
    }, [activeTab]);

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 10000);

        // Request Notification Permission
        if ("Notification" in window) {
            Notification.requestPermission();
        }

        fetchHistory();
        fetchTraining();

        return () => {
            clearInterval(interval);
        };
    }, [token]);

    const fetchHistory = async () => {
        try {
            const resp = await fetch(`${API_BASE}/history?token=${token}`);
            const data = await resp.json();
            setHistory(data.reverse());
        } catch (e) { console.error(e); }
    };

    const fetchTraining = async () => {
        try {
            const resp = await fetch(`${API_BASE}/training/scenarios?token=${token}`);
            const data = await resp.json();
            setTrainingScenarios(data);
        } catch (e) { console.error(e); }
    };

    const handleCheckTraining = async (verdict) => {
        const scenario = trainingScenarios[currentScenarioIdx];
        setIsTrainingLoading(true);
        try {
            const resp = await fetch(`${API_BASE}/training/check?scenario_id=${scenario.id}&verdict=${verdict}&token=${token}`, {
                method: 'POST'
            });
            const data = await resp.json();
            setTrainingFeedback(data);
            if (data.is_correct) {
                setScoreCount(prev => prev + 1);
            }
        } catch (e) { console.error(e); }
        finally { setIsTrainingLoading(false); }
    };

    const handleNextScenario = () => {
        setTrainingFeedback(null);
        if (currentScenarioIdx === trainingScenarios.length - 1) {
            setTestCompleted(true);
        } else {
            setCurrentScenarioIdx((prev) => prev + 1);
        }
    };

    const handleRestartTest = () => {
        setTestCompleted(false);
        setCurrentScenarioIdx(0);
        setScoreCount(0);
        setTrainingFeedback(null);
    };

    const handleDownloadAwarenessReport = () => {
        window.open(`${API_BASE}/report/awareness?token=${token}`, '_blank');
    };

    const handleDownloadReport = async (data) => {
        setIsReporting(true);
        try {
            const resp = await fetch(`${API_BASE}/report/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const { download_url } = await resp.json();
            window.open(`${API_BASE}${download_url}`, '_blank');
        } catch (e) { console.error(e); }
        finally { setIsReporting(false); }
    };

    const handleFeedback = async (label) => {
        try {
            await fetch(`${API_BASE}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: inputText,
                    initial_score: result.risk_score,
                    user_label: label,
                    confidence: result.confidence
                })
            });
            alert("Feedback recorded. Thank you for helping the AI learn!");
        } catch (e) { console.error(e); }
    };

    const fetchMetrics = async () => {
        try {
            const resp = await fetch(`${API_BASE}/metrics?token=${token}`);
            const data = await resp.json();
            setMetrics(data);
        } catch (e) { console.error(e); }
    };

    const handleAnalyze = async () => {
        if (!inputText.trim()) return;
        setIsAnalyzing(true);
        try {
            const resp = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: inputText, token: token })
            });
            const data = await resp.json();
            setResult(data);

            // Trigger Notification for High Risk Phishing
            if (data.risk_score > 70 && Notification.permission === "granted") {
                new Notification("🚨 High Risk Threat Detected", {
                    body: `Phishing attempt identified with ${data.risk_score}% risk score. Category: ${data.category}`,
                    icon: "/shield-logo.png"
                });
            }

            fetchMetrics();
        } catch (e) {
            console.error(e);
            alert("Error analyzing message. Is the backend running?");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleScriptAnalyze = async () => {
        if (!scriptInput.trim()) return;
        setIsScriptAnalyzing(true);
        try {
            const resp = await fetch(`${API_BASE}/script/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: scriptInput })
            });
            const data = await resp.json();
            setScriptResult(data);
        } catch (e) {
            console.error(e);
            alert("Error analyzing script.");
        } finally {
            setIsScriptAnalyzing(false);
        }
    };



    const getRiskColor = (score) => {
        if (score > 70) return "text-red-500";
        if (score > 30) return "text-yellow-500";
        return "text-green-500";
    };

    const lineData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
            {
                label: 'Threats Detected',
                data: [12, 19, 3, 5, 2, 3, 7],
                fill: true,
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderColor: '#3b82f6',
                tension: 0.4,
            },
        ],
    };

    if (!metrics) {
        return (
            <div className="min-h-screen bg-[#0a0c10] flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-400 font-bold animate-pulse">Initializing ZenShield AI Intelligence...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-screen bg-[#0a0c10] text-gray-200 overflow-hidden font-sans">
            {/* Sidebar */}
            <div className="w-64 bg-[#11141b] border-r border-gray-800 flex flex-col">
                <div className="p-6 flex items-center gap-3">
                    <div className="w-10 h-10 bg-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-orange-900/20">
                        <Shield className="text-white w-6 h-6" />
                    </div>
                    <span className="font-display font-bold text-xl tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        ZenShield
                        <span className="text-orange-500 block text-xs -mt-1 uppercase tracking-widest font-black">Cybersecurity AI</span>
                    </span>
                </div>

                <nav className="flex-1 mt-6 px-4 space-y-2">
                    {[
                        { id: 'analyze', icon: Search, label: 'Phishing Analysis' },
                        { id: 'script-audit', icon: FileIcon, label: 'Script Audit' },
                        { id: 'training', icon: Zap, label: 'AI Training' },
                        { id: 'history', icon: BarChart3, label: 'Threat History' },
                    ].map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${activeTab === item.id
                                ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                                : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                                }`}
                        >
                            <item.icon size={20} />
                            <span className="font-medium">{item.label}</span>
                        </button>
                    ))}
                </nav>

                <div className="p-6 border-t border-gray-800">
                    <div className="bg-[#1a1f29] rounded-xl p-4 border border-gray-800">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                                <Activity className="text-blue-500 w-4 h-4" />
                                <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Security Awareness</span>
                            </div>
                            <span className={`text-xs font-black ${metrics?.awareness_stats?.current_score > 70 ? 'text-green-500' : 'text-red-500'}`}>
                                {metrics?.awareness_stats?.current_score}%
                            </span>
                        </div>
                        <div className="h-2 w-full bg-gray-900 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${metrics?.awareness_stats?.current_score}%` }}
                                className={`h-full ${metrics?.awareness_stats?.current_score > 70 ? 'bg-green-500' : 'bg-orange-500'}`}
                            />
                        </div>
                        <p className="mt-3 text-[10px] text-gray-500 leading-tight uppercase font-bold tracking-tighter">
                            {metrics?.awareness_stats?.current_score > 80 ? 'Highly Resilient' : 'Needs Interactive Training'}
                        </p>
                    </div>
                </div>

                <div className="p-4 border-t border-gray-800">
                    <div className="flex items-center gap-3 px-2 py-3">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-xs font-black">
                            {user?.username?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs font-bold text-white truncate">{user?.username || 'User'}</p>
                            <p className="text-[10px] text-gray-500 truncate">{user?.email || ''}</p>
                        </div>
                        <button
                            onClick={onLogout}
                            className="p-2 text-gray-500 hover:text-red-400 transition-colors rounded-lg hover:bg-red-500/10"
                            title="Sign Out"
                        >
                            <ChevronRight size={14} className="rotate-90" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
                <AnimatePresence mode="wait">
                    {activeTab === 'script-audit' && (
                        <motion.div
                            key="script-audit"
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.98 }}
                            className="max-w-6xl mx-auto space-y-8"
                        >
                            <header className="flex justify-between items-start">
                                <div>
                                    <h1 className="text-3xl font-display font-bold text-white mb-2">Malicious Script Audit</h1>
                                    <p className="text-gray-400">Deep packet inspection for suspicious code fragments.</p>
                                </div>
                                <div className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-2xl flex items-center gap-3">
                                    <Cpu className="text-orange-400" size={24} />
                                    <div>
                                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest">NPU Acceleration</p>
                                        <p className="text-xs font-bold text-white">AMD Ryzen™ AI-Assisted Scan</p>
                                    </div>
                                </div>
                            </header>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <div className="lg:col-span-2 space-y-6">
                                    <div className="bg-[#11141b] rounded-2xl border border-gray-800 shadow-2xl overflow-hidden font-mono">
                                        <div className="bg-[#0d1016] px-6 py-3 border-b border-gray-800 flex justify-between items-center">
                                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Source Code (Python/JS)</span>
                                            <div className="flex gap-1.5">
                                                <div className="w-2.5 h-2.5 rounded-full bg-red-500/20"></div>
                                                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20"></div>
                                                <div className="w-2.5 h-2.5 rounded-full bg-green-500/20"></div>
                                            </div>
                                        </div>
                                        <textarea
                                            value={scriptInput}
                                            onChange={(e) => setScriptInput(e.target.value)}
                                            placeholder="Paste script here (e.g. import os; os.system('...'))"
                                            className="w-full bg-transparent p-6 h-96 focus:outline-none resize-none text-sm text-blue-300"
                                        />
                                        <div className="p-4 border-t border-gray-800 flex justify-end bg-[#0d1016]">
                                            <button
                                                onClick={handleScriptAnalyze}
                                                disabled={isScriptAnalyzing || !scriptInput.trim()}
                                                className="bg-orange-600 hover:bg-orange-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all"
                                            >
                                                {isScriptAnalyzing ? <RefreshCw className="animate-spin" /> : <Eye size={18} />}
                                                {isScriptAnalyzing ? "Scanning..." : "Audit Code"}
                                            </button>
                                        </div>
                                    </div>

                                    {scriptResult && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="bg-[#11141b] border border-gray-800 rounded-2xl p-8 shadow-2xl"
                                        >
                                            <div className="flex justify-between items-center mb-8">
                                                <div>
                                                    <h2 className="text-4xl font-black text-white italic">{scriptResult.verdict}</h2>
                                                    <div className="flex items-center gap-2 mt-2">
                                                        <Zap size={14} className="text-orange-500" />
                                                        <span className="text-[10px] text-orange-500 font-bold uppercase tracking-widest">{scriptResult.acceleration_mode}</span>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1">Threat Score</p>
                                                    <p className={`text-4xl font-black ${scriptResult.threat_score > 60 ? 'text-red-500' : 'text-orange-500'}`}>{scriptResult.threat_score}%</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                {(scriptResult.findings || []).map((f, i) => (
                                                    <div key={i} className="bg-[#0d1016] border border-gray-800 p-6 rounded-2xl">
                                                        <div className="flex justify-between items-center mb-4">
                                                            <span className="text-[10px] px-3 py-1 bg-red-500/10 text-red-500 border border-red-500/20 rounded-full font-black uppercase tracking-widest">{f.category}</span>
                                                            <span className="text-xs text-gray-600">Risk: {f.risk_level}</span>
                                                        </div>
                                                        <div className="space-y-2">
                                                            {(f.triggers || []).map((t, idx) => (
                                                                <code key={idx} className="block text-xs text-orange-400 bg-orange-950/10 p-2 rounded border border-orange-950/20">{t}</code>
                                                            ))}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                            <div className="mt-8 pt-8 border-t border-gray-800 space-y-6">
                                                <h3 className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider">
                                                    <CheckCircle2 className="text-orange-500" size={16} />
                                                    Code Security Assessment
                                                </h3>
                                                <p className="text-sm text-gray-300 leading-relaxed font-medium">
                                                    {scriptResult.plain_explanation}
                                                </p>
                                                <RecommendationPanel recommendations={scriptResult.recommendations} severity={scriptResult.severity} />
                                                <button
                                                    onClick={() => handleDownloadReport(scriptResult)}
                                                    className="w-full mt-6 bg-orange-600/10 hover:bg-orange-600/20 text-orange-500 text-[10px] font-black uppercase tracking-widest py-3 rounded-xl border border-orange-500/20 flex items-center justify-center gap-2 transition-all"
                                                >
                                                    {isReporting ? <RefreshCw size={12} className="animate-spin" /> : <Download size={12} />}
                                                    Export Full Audit PDF
                                                </button>
                                            </div>
                                        </motion.div>
                                    )}
                                </div>

                                <div className="space-y-8">
                                    <div className="bg-[#11141b] rounded-2xl p-6 border border-gray-800">
                                        <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                                            <Info size={16} className="text-orange-500" />
                                            Audit Handbook
                                        </h3>
                                        <ul className="space-y-4">
                                            {[
                                                { t: 'Data Exfil', d: 'Detection of remote POST/GET requests to non-whitelisted IPs.' },
                                                { t: 'System Mod', d: 'Identifying calls to OS-level modification flags.' },
                                                { t: 'Obfuscation', d: 'Spotting Base64 or Zlib encoding used to hide payloads.' },
                                                { t: 'Side-Channel', d: 'AMD-specific detection of branch prediction timing leaks.' }
                                            ].map((item, i) => (
                                                <li key={i}>
                                                    <p className="text-xs font-black text-gray-300 uppercase tracking-tighter mb-1">{item.t}</p>
                                                    <p className="text-[11px] text-gray-500 leading-tight">{item.d}</p>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}



                    {activeTab === 'analyze' && (
                        <motion.div
                            key="analyze"
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.98 }}
                            className="max-w-6xl mx-auto space-y-8"
                        >
                            <header className="flex justify-between items-start">
                                <div>
                                    <h1 className="text-3xl font-display font-bold text-white mb-2">Threat Analysis Engine</h1>
                                    <p className="text-gray-400">Perform a multi-layered AI audit on messages or URLs.</p>
                                </div>
                            </header>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <div className="lg:col-span-2 space-y-6">
                                    <div className="bg-[#11141b] rounded-2xl p-1 border border-gray-800 shadow-2xl">
                                        <textarea
                                            value={inputText}
                                            onChange={(e) => setInputText(e.target.value)}
                                            placeholder="Paste suspicious text or URL here..."
                                            className="w-full bg-transparent p-6 h-64 focus:outline-none resize-none text-lg text-gray-200"
                                        />
                                        <div className="p-4 border-t border-gray-800 flex justify-between items-center bg-[#0d1016] rounded-b-2xl">
                                            <div className="flex gap-4 items-center">
                                                <div className="flex items-center gap-2 text-xs text-gray-500">
                                                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                                    Hybrid AI Model
                                                </div>
                                                <div className="h-4 w-px bg-gray-800"></div>
                                                <label className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 cursor-pointer group transition-all">
                                                    <ImageIcon size={14} className="group-hover:scale-110 transition-transform" />
                                                    <span>{isVisionAnalyzing ? 'Auditing...' : 'Audit Image'}</span>
                                                    <input
                                                        type="file"
                                                        className="hidden"
                                                        accept="image/*"
                                                        onChange={handleImageUpload}
                                                        disabled={isVisionAnalyzing}
                                                    />
                                                </label>
                                            </div>
                                            <button
                                                onClick={handleAnalyze}
                                                disabled={isAnalyzing || (!inputText.trim() && !visionResult)}
                                                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-900/20"
                                            >
                                                {isAnalyzing ? <RefreshCw className="animate-spin" /> : <Zap size={18} />}
                                                {isAnalyzing ? "Processing..." : "Analyze Now"}
                                            </button>
                                        </div>
                                    </div>

                                    {(result || visionResult) && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="bg-[#11141b] border border-gray-800 rounded-2xl overflow-hidden shadow-2xl"
                                        >
                                            <div className={`h-1.5 w-full ${(visionResult?.final_risk_score || result?.risk_score) > 70 ? 'bg-red-500' : (visionResult?.final_risk_score || result?.risk_score) > 30 ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
                                            <div className="p-8">
                                                <div className="flex justify-between items-start mb-8">
                                                    <div>
                                                        <div className="flex items-center gap-3 mb-2">
                                                            <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${(visionResult?.final_risk_score || result?.risk_score) > 70 ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                                                                (visionResult?.final_risk_score || result?.risk_score) > 30 ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' :
                                                                    'bg-green-500/10 text-green-500 border-green-500/20'
                                                                }`}>
                                                                {result?.category || (visionResult ? 'Vision Audit' : 'Analysis')}
                                                            </span>
                                                            <span className="text-gray-500 text-sm">• Latency: {result?.latency || '24ms'}</span>
                                                        </div>
                                                        <h2 className="text-6xl font-black text-white">
                                                            {visionResult ? visionResult.final_risk_score : result?.risk_score}% <span className="text-2xl font-medium text-gray-500">Risk</span>
                                                        </h2>
                                                        <div className="flex items-center gap-2 mt-4">
                                                            <Zap size={14} className="text-blue-400" />
                                                            <span className="text-[10px] text-blue-400 font-bold uppercase tracking-widest">
                                                                {result?.acceleration_mode || visionResult?.acceleration_mode || "AMD ROCm Optimized (NPU-Accelerated)"}
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-gray-400 text-xs mb-1 uppercase tracking-widest font-black">AI Confidence</p>
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-32 h-2 bg-gray-800 rounded-full overflow-hidden">
                                                                <div className="h-full bg-blue-500" style={{ width: `${(result?.confidence || 0.98) * 100}%` }}></div>
                                                            </div>
                                                            <span className="font-mono text-white font-bold">{((result?.confidence || 0.98) * 100).toFixed(0)}%</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                {visionResult && (
                                                    <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-gray-800">
                                                            <div className="flex items-center gap-3 mb-3">
                                                                <Camera size={16} className="text-purple-400" />
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Forgery Analysis (ELA)</p>
                                                            </div>
                                                            <div className="flex items-end justify-between">
                                                                <span className="text-xl font-black text-white">{visionResult.vision.manipulation_score}%</span>
                                                                <span className="text-[10px] text-gray-600">Manipulation Conf.</span>
                                                            </div>
                                                            <div className="mt-2 h-1 w-full bg-gray-900 rounded-full overflow-hidden">
                                                                <div className={`h-full ${visionResult.vision.manipulation_score > 50 ? 'bg-red-500' : 'bg-purple-500'}`} style={{ width: `${visionResult.vision.manipulation_score}%` }}></div>
                                                            </div>
                                                        </div>
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-gray-800">
                                                            <div className="flex items-center gap-3 mb-3">
                                                                <ImageIcon size={16} className="text-blue-400" />
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">OCR Extraction</p>
                                                            </div>
                                                            <p className="text-xs text-gray-400 line-clamp-2">
                                                                {visionResult.vision.extracted_text || "No text detected in image."}
                                                            </p>
                                                        </div>
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-orange-500/20">
                                                            <div className="flex items-center gap-3 mb-3">
                                                                <Monitor size={16} className="text-orange-400" />
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Deepfake UI Audit</p>
                                                            </div>
                                                            <div className="flex items-end justify-between">
                                                                <span className="text-xl font-black text-white">{visionResult.vision.deepfake_ui_score}%</span>
                                                                <span className="text-[10px] text-gray-600">UI Inconsistency</span>
                                                            </div>
                                                            <div className="mt-2 h-1 w-full bg-gray-900 rounded-full overflow-hidden">
                                                                <div className="h-full bg-orange-500" style={{ width: `${visionResult.vision.deepfake_ui_score}%` }}></div>
                                                            </div>
                                                        </div>
                                                        {visionResult.vision.qr_codes?.length > 0 && (
                                                            <div className="col-span-1 md:col-span-2 lg:col-span-3 bg-[#0d1016] p-4 rounded-xl border border-blue-500/30">
                                                                <div className="flex items-center gap-3 mb-2">
                                                                    <Zap size={16} className="text-yellow-400" />
                                                                    <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">QR Intel Found</p>
                                                                </div>
                                                                <p className="text-xs font-mono text-blue-400 break-all bg-blue-900/10 p-2 rounded">
                                                                    {visionResult.vision.qr_codes[0].data}
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                                {result?.trigger_words && (
                                                    <div className="mb-8 p-6 bg-[#0d1016] border border-gray-800 rounded-2xl">
                                                        <h3 className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider mb-4">
                                                            <Eye className="text-red-500" size={16} />
                                                            Analyzed Evidence (XAI)
                                                        </h3>
                                                        <HighlightText text={inputText} triggers={result.trigger_words} />
                                                        <div className="mt-4 flex flex-wrap gap-2">
                                                            {result.trigger_words.map((word, i) => (
                                                                <span key={i} className="text-[9px] px-2 py-0.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full font-black uppercase tracking-widest">
                                                                    {word}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                                    <div className="space-y-6">
                                                        <h3 className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider">
                                                            <Layers className="text-blue-500" size={16} />
                                                            Risk Breakdown
                                                        </h3>
                                                        <div className="bg-[#1a1f29] rounded-2xl p-6 border border-gray-800 space-y-4">
                                                            <div className="space-y-2">
                                                                <div className="flex justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                                                    <span>ML Probability</span>
                                                                    <span className="text-blue-500">{result?.breakdown?.ml_probability || 0}%</span>
                                                                </div>
                                                                <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-blue-500" style={{ width: `${result?.breakdown?.ml_probability || 0}%` }}></div>
                                                                </div>
                                                            </div>
                                                            <div className="space-y-2">
                                                                <div className="flex justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                                                    <span>URL Risk Signals</span>
                                                                    <span className="text-purple-500">{result?.breakdown?.url_risk || 0}%</span>
                                                                </div>
                                                                <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-purple-500" style={{ width: `${result?.breakdown?.url_risk || 0}%` }}></div>
                                                                </div>
                                                            </div>
                                                            <div className="space-y-2">
                                                                <div className="flex justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest">
                                                                    <span>Heuristic Flags</span>
                                                                    <span className="text-green-500">{result?.breakdown?.text_heuristic?.total || result?.breakdown?.text_heuristic ? Object.values(result.breakdown.text_heuristic).reduce((a, b) => a + b, 0) / 4 : 0}%</span>
                                                                </div>
                                                                <div className="h-1 w-full bg-gray-800 rounded-full overflow-hidden">
                                                                    <div className="h-full bg-green-500" style={{ width: `${result?.breakdown?.text_heuristic ? Object.values(result.breakdown.text_heuristic).reduce((a, b) => a + b, 0) / 4 : 0}%` }}></div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {result?.plain_explanation && (
                                                        <div className="md:col-span-2 space-y-4">
                                                            <div className={`p-6 rounded-2xl border ${
                                                                result?.severity === 'High' ? 'bg-red-500/5 border-red-500/20' :
                                                                result?.severity === 'Medium' ? 'bg-yellow-500/5 border-yellow-500/20' :
                                                                'bg-green-500/5 border-green-500/20'
                                                            }`}>
                                                                <div className="flex items-center gap-3 mb-3">
                                                                    <AlertTriangle size={18} className={
                                                                        result?.severity === 'High' ? 'text-red-500' :
                                                                        result?.severity === 'Medium' ? 'text-yellow-500' : 'text-green-500'
                                                                    } />
                                                                    <h3 className="text-white font-bold text-sm uppercase tracking-wider">
                                                                        Why is this {result?.severity === 'Low' ? 'safe' : 'dangerous'}?
                                                                    </h3>
                                                                    {result?.threat_type && result.threat_type !== 'Safe' && (
                                                                        <span className={`ml-auto text-[9px] font-black uppercase tracking-widest px-3 py-1 rounded-full border ${
                                                                            result.threat_type === 'Phishing' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                                                            result.threat_type === 'Social Engineering' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                                                            result.threat_type === 'Financial Fraud' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                                                            'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                                                                        }`}>
                                                                            {result.threat_type}
                                                                        </span>
                                                                    )}
                                                                </div>
                                                                <p className="text-sm text-gray-300 leading-relaxed font-medium">
                                                                    {result.plain_explanation}
                                                                </p>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>

                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8 pt-8 border-t border-gray-800">
                                                    <div className="space-y-6">
                                                        <h3 className="flex items-center gap-2 text-white font-bold text-sm uppercase tracking-wider">
                                                            <CheckCircle2 className="text-blue-500" size={16} />
                                                            Threat Assessment
                                                        </h3>
                                                        <div className="p-6 rounded-2xl bg-[#1a1f29] border border-gray-800">
                                                            <p className="text-sm text-gray-300 leading-relaxed mb-6 font-medium">
                                                                {result?.plain_explanation || 'No assessment available for this audit.'}
                                                            </p>
                                                            <RecommendationPanel recommendations={result?.recommendations} severity={result?.severity} />
                                                            <div className="mt-6 flex gap-2">
                                                                <button
                                                                    onClick={() => handleDownloadReport(result || visionResult)}
                                                                    className="flex-1 bg-white/5 hover:bg-white/10 text-white text-[10px] font-black uppercase tracking-widest py-3 rounded-xl border border-white/10 flex items-center justify-center gap-2 transition-all"
                                                                >
                                                                    {isReporting ? <RefreshCw size={12} className="animate-spin" /> : <Download size={12} />}
                                                                    Detailed Audit PDF
                                                                </button>
                                                                {result && (
                                                                    <div className="flex gap-2">
                                                                        <button onClick={() => handleFeedback('correct')} className="p-3 bg-green-500/10 text-green-500 rounded-xl border border-green-500/20 hover:bg-green-500/20 transition-all"><ThumbsUp size={14} /></button>
                                                                        <button onClick={() => handleFeedback('incorrect')} className="p-3 bg-red-500/10 text-red-500 rounded-xl border border-red-500/20 hover:bg-red-500/20 transition-all"><ThumbsDown size={14} /></button>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                {result?.external_intel && (
                                                    <div className="px-8 pb-8 pt-8 border-t border-gray-800 mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-gray-800 flex items-center gap-4">
                                                            <div className="p-2 bg-blue-500/10 rounded-lg"><Globe size={20} className="text-blue-500" /></div>
                                                            <div>
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Domain Intel</p>
                                                                <p className="text-xs font-mono text-white">{result.external_intel.domain}</p>
                                                            </div>
                                                        </div>
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-gray-800 flex items-center gap-4">
                                                            <div className="p-2 bg-red-500/10 rounded-lg"><Shield size={20} className="text-red-500" /></div>
                                                            <div>
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">VirusTotal Node</p>
                                                                <p className="text-xs font-mono text-white">{result.external_intel.vt_score} Engines</p>
                                                            </div>
                                                        </div>
                                                        <div className="bg-[#0d1016] p-4 rounded-xl border border-gray-800 flex items-center gap-4">
                                                            <div className="p-2 bg-purple-500/10 rounded-lg"><Info size={20} className="text-purple-500" /></div>
                                                            <div>
                                                                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">WHOIS Age</p>
                                                                <p className="text-xs font-mono text-white">{result.external_intel.whois_age}</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </motion.div>
                                    )}
                                </div>

                                <div className="space-y-8">
                                    <div className="bg-[#11141b] rounded-2xl p-6 border border-gray-800 shadow-xl">
                                        <h3 className="text-gray-500 text-[10px] font-black uppercase tracking-[.2em] mb-4">Pipeline Metrics</h3>
                                        <div className="space-y-4">
                                            <div className="flex justify-between items-end border-b border-gray-800/50 pb-3">
                                                <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Latency</span>
                                                <span className="font-mono text-blue-400 font-bold">{result?.latency || 'N/A'}</span>
                                            </div>
                                            <div className="flex justify-between items-end border-b border-gray-800/50 pb-3">
                                                <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Analyzed Today</span>
                                                <span className="font-mono text-purple-400 font-bold">{metrics?.total_analyzed || '0'}</span>
                                            </div>
                                            <div className="flex justify-between items-end">
                                                <span className="text-xs text-gray-500 font-bold uppercase tracking-wider">Acc Rating</span>
                                                <span className="font-mono text-green-400 font-bold">{metrics?.model_accuracy || '98.4%'}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-2xl p-6 border border-blue-500/20">
                                        <div className="flex items-center gap-3 mb-4">
                                            <Cpu className="text-blue-400" size={20} />
                                            <span className="font-bold text-white text-sm">Security Layer Stack</span>
                                        </div>
                                        <ul className="space-y-3">
                                            {['NLP Transformer Node', 'URL Intelligence API', 'Heuristic Engine', 'Explainability Layer'].map((l, i) => (
                                                <li key={i} className="flex items-center gap-3 text-xs text-blue-300/80">
                                                    <div className="w-1 h-1 bg-blue-500 rounded-full"></div>
                                                    {l}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* Intrusion Tab Removed */}









                    {activeTab === 'training' && (
                        <motion.div
                            key="training"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="max-w-4xl mx-auto space-y-8"
                        >
                            <header className="flex justify-between items-center">
                                <div>
                                    <h1 className="text-3xl font-display font-bold text-white mb-2">Security Awareness Exam</h1>
                                    <p className="text-gray-400">Complete all 10 scenarios to receive your security certification.</p>
                                </div>
                                <div className="flex gap-4">
                                    <div className="px-4 py-2 bg-gray-900 border border-gray-800 rounded-xl">
                                        <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest mr-2">Progress</span>
                                        <span className="text-sm font-mono text-blue-400 font-bold">{currentScenarioIdx + 1}/10</span>
                                    </div>
                                    <div className="px-6 py-3 bg-blue-600/10 border border-blue-600/20 rounded-2xl">
                                        <span className="text-xs font-black text-blue-400 uppercase tracking-widest">Global Rank: {metrics?.awareness_stats?.current_score}%</span>
                                    </div>
                                </div>
                            </header>

                            {!testCompleted ? (
                                trainingScenarios.length > 0 ? (
                                    <div className="bg-[#11141b] rounded-3xl border border-gray-800 shadow-2xl overflow-hidden">
                                        <div className="p-8 border-b border-gray-800 bg-gray-900/20 flex justify-between items-center">
                                            <h3 className="text-white font-bold">{trainingScenarios[currentScenarioIdx].title}</h3>
                                            <span className={`text-[10px] font-black uppercase px-2 py-1 rounded ${
                                                trainingScenarios[currentScenarioIdx].difficulty === 'Easy' ? 'bg-green-500/10 text-green-500' :
                                                trainingScenarios[currentScenarioIdx].difficulty === 'Medium' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-red-500/10 text-red-500'
                                            }`}>
                                                {trainingScenarios[currentScenarioIdx].difficulty}
                                            </span>
                                        </div>
                                        <div className="p-10">
                                            <div className="bg-[#0a0c10] rounded-2xl p-8 border border-gray-800 mb-8 font-mono text-sm whitespace-pre-wrap text-blue-300/80 leading-relaxed min-h-[120px]">
                                                {trainingScenarios[currentScenarioIdx].content}
                                            </div>

                                            {!trainingFeedback ? (
                                                <div className="grid grid-cols-2 gap-6">
                                                    <button
                                                        onClick={() => handleCheckTraining('safe')}
                                                        className="py-4 bg-green-600/10 hover:bg-green-600/20 text-green-500 border border-green-500/20 rounded-2xl font-black uppercase tracking-widest text-xs transition-all"
                                                    >
                                                        Looks Safe
                                                    </button>
                                                    <button
                                                        onClick={() => handleCheckTraining('danger')}
                                                        className="py-4 bg-red-600/10 hover:bg-red-600/20 text-red-500 border border-red-500/20 rounded-2xl font-black uppercase tracking-widest text-xs transition-all"
                                                    >
                                                        Report Phishing
                                                    </button>
                                                </div>
                                            ) : (
                                                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                                                    <div className={`p-6 rounded-2xl border ${trainingFeedback.is_correct ? 'bg-green-600/10 border-green-500/20' : 'bg-red-600/10 border-red-500/20'}`}>
                                                        <div className="flex items-center gap-3 mb-2">
                                                            {trainingFeedback.is_correct ? <CheckCircle2 className="text-green-500" /> : <AlertTriangle className="text-red-500" />}
                                                            <h4 className={`font-black uppercase tracking-widest text-sm ${trainingFeedback.is_correct ? 'text-green-500' : 'text-red-500'}`}>
                                                                {trainingFeedback.is_correct ? "Correct Analysis" : "Incorrect Analysis"}
                                                            </h4>
                                                        </div>
                                                        <p className="text-sm text-gray-300">{trainingFeedback.explanation}</p>
                                                    </div>

                                                    {trainingFeedback.red_flags.length > 0 && (
                                                        <div className="bg-[#1a1f29] p-6 rounded-2xl border border-gray-800">
                                                            <h5 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Key Indicators</h5>
                                                            <div className="space-y-3">
                                                                {trainingFeedback.red_flags.map((flag, i) => (
                                                                    <div key={i} className="flex gap-3 text-xs text-gray-400">
                                                                        <span className="text-red-500">•</span>
                                                                        {flag}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    <button
                                                        onClick={handleNextScenario}
                                                        className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center gap-2"
                                                    >
                                                        {currentScenarioIdx === 9 ? "Finish Exam" : "Next Question"} <ChevronRight size={16} />
                                                    </button>
                                                </motion.div>
                                            )}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="h-64 flex flex-col items-center justify-center text-gray-600 border border-dashed border-gray-800 rounded-3xl">
                                        <RefreshCw className="mb-4 animate-spin opacity-20" size={40} />
                                        <p className="uppercase tracking-widest font-black opacity-30">Loading training scenarios...</p>
                                        <button onClick={fetchTraining} className="mt-4 text-[10px] text-blue-500 hover:underline">Retry Connection</button>
                                    </div>
                                )
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="bg-[#11141b] rounded-3xl border border-gray-800 shadow-2xl overflow-hidden p-12 text-center"
                                >
                                    <div className="w-24 h-24 bg-blue-600/10 rounded-full flex items-center justify-center mx-auto mb-6">
                                        <Zap className="text-blue-500" size={48} />
                                    </div>
                                    <h2 className="text-4xl font-display font-bold text-white mb-2">Exam Complete</h2>
                                    <p className="text-gray-400 mb-8">You have completed the ZenShield Security Awareness Training.</p>
                                    
                                    <div className="max-w-md mx-auto grid grid-cols-2 gap-8 mb-12">
                                        <div className="bg-[#0a0c10] p-8 rounded-3xl border border-gray-800">
                                            <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Correct Answers</p>
                                            <p className="text-4xl font-black text-white">{scoreCount}/10</p>
                                        </div>
                                        <div className="bg-[#0a0c10] p-8 rounded-3xl border border-gray-800">
                                            <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Percentage</p>
                                            <p className="text-4xl font-black text-blue-500">{(scoreCount / 10) * 100}%</p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={handleRestartTest}
                                        className="px-12 py-4 bg-white text-black rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-gray-200 transition-all shadow-xl shadow-white/5"
                                    >
                                        Retake Security Exam
                                    </button>
                                </motion.div>
                            )}
                        </motion.div>
                    )}

                    {activeTab === 'history' && (
                        <motion.div
                            key="history"
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="max-w-6xl mx-auto space-y-8"
                        >
                            <header className="flex justify-between items-center">
                                <div>
                                    <h1 className="text-3xl font-display font-bold text-white mb-2">Threat Intelligence History</h1>
                                    <p className="text-gray-400">Trend analysis and historical scan data.</p>
                                </div>
                                <button
                                    onClick={handleDownloadAwarenessReport}
                                    className="flex items-center gap-3 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-widest text-xs transition-all shadow-lg shadow-blue-900/40"
                                >
                                    <Download size={18} />
                                    Export Awareness Report
                                </button>
                            </header>

                            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                                <div className="lg:col-span-1 space-y-6">
                                    <div className="bg-[#11141b] rounded-3xl p-8 border border-gray-800 shadow-xl">
                                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Total Scans</p>
                                        <h3 className="text-5xl font-black text-white">{history.length}</h3>
                                        <div className="mt-4 pt-4 border-t border-gray-800">
                                            <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2">Risk Distribution</p>
                                            <div className="space-y-3">
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-red-500">High Risk</span>
                                                    <span className="text-white text-right">{history.filter(h => h.result.risk_score > 70).length}</span>
                                                </div>
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-orange-500">Medium</span>
                                                    <span className="text-white text-right">{history.filter(h => h.result.risk_score <= 70 && h.result.risk_score > 30).length}</span>
                                                </div>
                                                <div className="flex justify-between text-xs">
                                                    <span className="text-green-500">Verified Safe</span>
                                                    <span className="text-white text-right">{history.filter(h => h.result.risk_score <= 30).length}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-[#11141b] rounded-3xl p-8 border border-gray-800 shadow-xl h-64">
                                        <p className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-4">Awareness Progress</p>
                                        <Line
                                            data={{
                                                labels: metrics?.awareness_stats?.trend?.map(t => t.date) || [],
                                                datasets: [{
                                                    label: 'Awareness Score',
                                                    data: metrics?.awareness_stats?.history_points || [],
                                                    borderColor: '#3b82f6',
                                                    borderWidth: 3,
                                                    pointRadius: 2,
                                                    tension: 0.4,
                                                    fill: true,
                                                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
                                                }]
                                            }}
                                            options={{
                                                maintainAspectRatio: false,
                                                plugins: { 
                                                    legend: { display: false },
                                                    tooltip: { enabled: true }
                                                },
                                                scales: {
                                                    y: { display: true, beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#444' } },
                                                    x: { display: false }
                                                }
                                            }}
                                        />
                                    </div>

                                    <button 
                                        onClick={handleDownloadAwarenessReport}
                                        className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20"
                                    >
                                        <Download size={14} />
                                        Export Global Security Report
                                    </button>
                                </div>

                                <div className="lg:col-span-3">
                                    <div className="bg-[#11141b] rounded-3xl border border-gray-800 shadow-xl overflow-hidden">
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-left">
                                                <thead className="bg-gray-900/50 border-b border-gray-800">
                                                    <tr>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest">Type</th>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest">Snippet</th>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest">Severity</th>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest">Score</th>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest">Result</th>
                                                        <th className="px-6 py-4 text-[10px] font-black text-gray-500 uppercase tracking-widest text-right">Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-gray-800">
                                                    {history.map((entry) => (
                                                        <tr key={entry.id} className="hover:bg-white/5 transition-colors">
                                                            <td className="px-6 py-4">
                                                                <span className="px-2 py-0.5 rounded bg-blue-900/20 text-blue-400 text-[10px] font-black uppercase tracking-tighter">
                                                                    {entry.type.replace('_', ' ')}
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4 text-xs font-mono text-gray-400 truncate max-w-[200px]">
                                                                {entry.result.text_preview}
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                <span className={`text-[10px] font-black uppercase ${entry.result.severity === 'High' ? 'text-red-500' :
                                                                        entry.result.severity === 'Medium' ? 'text-orange-500' : 'text-green-500'
                                                                    }`}>
                                                                    {entry.result.severity}
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4 font-mono text-xs text-white">
                                                                {entry.result.risk_score}%
                                                            </td>
                                                            <td className="px-6 py-4 text-[10px] font-black text-gray-300 uppercase">
                                                                {entry.result.verdict}
                                                            </td>
                                                            <td className="px-6 py-4 text-right">
                                                                <button
                                                                    onClick={() => handleDownloadReport(entry.result)}
                                                                    className="p-2 text-blue-500 hover:text-blue-400 transition-colors"
                                                                    title="Download Audit Report"
                                                                >
                                                                    <Download size={14} />
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>
        </div>
    );
};

const LoginPage = ({ onLogin }) => {
    const [isSignup, setIsSignup] = useState(false);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const endpoint = isSignup ? '/auth/signup' : '/auth/login';
            const body = isSignup
                ? { username, email, password }
                : { username, password };

            const resp = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const data = await resp.json();

            if (!resp.ok) {
                setError(data.detail || 'Authentication failed');
                return;
            }

            localStorage.setItem('zen_token', data.token);
            localStorage.setItem('zen_user', JSON.stringify(data.user));
            onLogin(data.user, data.token);
        } catch (err) {
            setError('Server connection failed. Is the backend running?');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0c10] flex items-center justify-center p-4">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/5 rounded-full blur-3xl"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="relative w-full max-w-md"
            >
                <div className="bg-[#11141b] border border-gray-800 rounded-3xl shadow-2xl overflow-hidden">
                    <div className="p-8 bg-gradient-to-b from-blue-600/10 to-transparent border-b border-gray-800">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                                <Shield size={20} className="text-white" />
                            </div>
                            <div>
                                <h1 className="text-xl font-bold text-white">ZenShield AI</h1>
                                <p className="text-[10px] text-blue-400 font-black uppercase tracking-widest">AMD ROCm Security Platform</p>
                            </div>
                        </div>
                    </div>

                    <div className="p-8">
                        <div className="flex bg-[#0a0c10] rounded-xl p-1 mb-8">
                            <button
                                onClick={() => { setIsSignup(false); setError(''); }}
                                className={`flex-1 py-2.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${!isSignup ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                            >
                                Sign In
                            </button>
                            <button
                                onClick={() => { setIsSignup(true); setError(''); }}
                                className={`flex-1 py-2.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all ${isSignup ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
                            >
                                Sign Up
                            </button>
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl"
                            >
                                <div className="flex items-center gap-2">
                                    <AlertTriangle size={14} className="text-red-500" />
                                    <p className="text-xs text-red-400 font-medium">{error}</p>
                                </div>
                            </motion.div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div>
                                <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2 block">
                                    {isSignup ? 'Username' : 'Username or Email'}
                                </label>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder={isSignup ? 'Choose a username' : 'Enter username or email'}
                                    className="w-full bg-[#0a0c10] border border-gray-800 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-600 transition-colors"
                                    required
                                />
                            </div>

                            {isSignup && (
                                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                                    <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2 block">Email</label>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="your@email.com"
                                        className="w-full bg-[#0a0c10] border border-gray-800 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-600 transition-colors"
                                        required={isSignup}
                                    />
                                </motion.div>
                            )}

                            <div>
                                <label className="text-[10px] text-gray-500 font-black uppercase tracking-widest mb-2 block">Password</label>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder={isSignup ? 'Min 6 characters' : 'Enter password'}
                                    className="w-full bg-[#0a0c10] border border-gray-800 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-600 transition-colors"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full py-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl font-black uppercase tracking-widest text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-900/30"
                            >
                                {isLoading ? (
                                    <><RefreshCw size={14} className="animate-spin" /> Authenticating...</>
                                ) : (
                                    <><Lock size={14} /> {isSignup ? 'Create Account' : 'Sign In'}</>
                                )}
                            </button>
                        </form>

                        <p className="text-center text-[10px] text-gray-600 mt-6">
                            {isSignup ? 'Already have an account?' : "Don't have an account?"}
                            <button
                                onClick={() => { setIsSignup(!isSignup); setError(''); }}
                                className="text-blue-500 hover:text-blue-400 ml-1 font-bold"
                            >
                                {isSignup ? 'Sign In' : 'Sign Up'}
                            </button>
                        </p>
                    </div>
                </div>

                <p className="text-center text-[10px] text-gray-700 mt-6 font-medium">
                    Powered by AMD ROCm Hardware-Accelerated AI Engine
                </p>
            </motion.div>
        </div>
    );
};

const App = () => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [authChecked, setAuthChecked] = useState(false);

    useEffect(() => {
        const savedToken = localStorage.getItem('zen_token');
        const savedUser = localStorage.getItem('zen_user');
        if (savedToken && savedUser) {
            setToken(savedToken);
            setUser(JSON.parse(savedUser));
        }
        setAuthChecked(true);
    }, []);

    const handleLogin = (userData, authToken) => {
        setUser(userData);
        setToken(authToken);
    };

    const handleLogout = () => {
        localStorage.removeItem('zen_token');
        localStorage.removeItem('zen_user');
        setUser(null);
        setToken(null);
    };

    if (!authChecked) {
        return (
            <div className="min-h-screen bg-[#0a0c10] flex items-center justify-center">
                <RefreshCw className="text-blue-500 animate-spin" size={32} />
            </div>
        );
    }

    if (!user) {
        return <LoginPage onLogin={handleLogin} />;
    }

    return <Dashboard user={user} token={token} onLogout={handleLogout} />;
};

export default App;
