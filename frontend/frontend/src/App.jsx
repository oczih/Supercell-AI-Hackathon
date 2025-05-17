import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import axios from 'axios';
import Loader from './components/Loader';
import WordCloud from './components/Wordcloud';
import ThemeDistribution from './components/ThemeDistribution';
import TopComments from './components/TopComments';
import DeveloperInsights from './components/DeveloperInsights';
import SettingsPanel from './components/SettingsPanel';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [sentimentData, setSentimentData] = useState([]);
  const [topComments, setTopComments] = useState([]);
  const [themeDistribution, setThemeDistribution] = useState({});
  const [wordcloudImage, setWordcloudImage] = useState('');
  const [developerInsights, setDeveloperInsights] = useState({});
  const [activeTab, setActiveTab] = useState(0);
  const [timePeriod, setTimePeriod] = useState('day');
  const [dataSource, setDataSource] = useState('reddit');
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if data is loaded on component mount
    checkDataStatus();
  }, []);

  useEffect(() => {
    // Reload data when data source changes
    if (dataLoaded) {
      fetchAllData();
    }
  }, [dataSource, timePeriod, dataLoaded]);

  const checkDataStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`);
      const { posts_loaded, comments_loaded, analysis_loaded } = response.data;
      setDataLoaded(posts_loaded && comments_loaded && analysis_loaded);
    } catch (err) {
      console.error('Error checking data status:', err);
      setError('Failed to connect to the API server. Please ensure it is running.');
    }
  };

  const loadData = async (postsFile, commentsFile, analysisFile) => {
    setLoading(true);
    setError(null);
    
    try {
      await axios.post(`${API_URL}/load-data`, {
        posts_file: postsFile,
        comments_file: commentsFile,
        analysis_file: analysisFile
      });
      
      setDataLoaded(true);
      fetchAllData();
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data. Please check file paths and try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [
        trendingResponse,
        sentimentResponse,
        commentsResponse,
        themeResponse,
        wordcloudResponse,
        insightsResponse
      ] = await Promise.all([
        axios.get(`${API_URL}/trending-topics`),
        axios.get(`${API_URL}/sentiment-over-time?period=${timePeriod}`),
        axios.get(`${API_URL}/top-comments`),
        axios.get(`${API_URL}/theme-distribution`),
        axios.get(`${API_URL}/wordcloud`),
        axios.get(`${API_URL}/developer-insights`)
      ]);
      
      setTrendingTopics(trendingResponse.data);
      setSentimentData(sentimentResponse.data);
      setTopComments(commentsResponse.data);
      setThemeDistribution(themeResponse.data);
      setWordcloudImage(wordcloudResponse.data.image);
      setDeveloperInsights(insightsResponse.data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data from the API.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Custom tooltip for the sentiment chart
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded shadow-md">
          <p className="font-semibold">{formatDate(label)}</p>
          <p>Sentiment: {payload[0].value.toFixed(2)}</p>
          <p>Comments: {payload[0].payload.count}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800">GamePulse</h1>
          <p className="text-xl text-gray-600">Real-Time Community Feedback Analyzer</p>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700">
            <p>{error}</p>
          </div>
        )}

        {!dataLoaded ? (
          <SettingsPanel onLoadData={loadData} loading={loading} />
        ) : (
          <div className="bg-white rounded-slg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <div className="flex space-x-4">
                <select
                  value={dataSource}
                  onChange={(e) => setDataSource(e.target.value)}
                  className="px-4 py-2 border rounded-md"
                >
                  <option value="reddit">Reddit</option>
                  <option value="youtube" disabled>YouTube (Coming Soon)</option>
                  <option value="app_store" disabled>App Store (Coming Soon)</option>
                </select>
                
                <select
                  value={timePeriod}
                  onChange={(e) => setTimePeriod(e.target.value)}
                  className="px-4 py-2 border rounded-md"
                >
                  <option value="hour">Hourly</option>
                  <option value="day">Daily</option>
                  <option value="week">Weekly</option>
                </select>
              </div>
              
              <button
                onClick={fetchAllData}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </button>
            </div>
            
            <Tabs selectedIndex={activeTab} onSelect={(index) => setActiveTab(index)}>
              <TabList className="flex border-b mb-6">
                <Tab className="px-6 py-3 cursor-pointer">Dashboard</Tab>
                <Tab className="px-6 py-3 cursor-pointer">Comments</Tab>
                <Tab className="px-6 py-3 cursor-pointer">Developer Mode</Tab>
              </TabList>
              
              <TabPanel>
                {loading ? (
                  <Loader />
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Sentiment Over Time Chart */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h2 className="text-xl font-semibold mb-4">Sentiment Over Time</h2>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={sentimentData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            dataKey="timestamp" 
                            tickFormatter={formatDate}
                          />
                          <YAxis 
                            domain={[-1, 1]} 
                            ticks={[-1, -0.5, 0, 0.5, 1]} 
                            tickFormatter={(value) => value.toFixed(1)}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          <Line 
                            type="monotone" 
                            dataKey="sentiment" 
                            stroke="#8884d8" 
                            activeDot={{ r: 8 }} 
                            name="Sentiment Score"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                    
                    {/* Theme Distribution */}
                    <ThemeDistribution data={themeDistribution} />
                    
                    {/* Word Cloud */}
                    <WordCloud imageUrl={wordcloudImage} />
                    
                    {/* Trending Topics */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h2 className="text-xl font-semibold mb-4">Trending Topics</h2>
                      <div className="flex flex-wrap gap-2">
                        {trendingTopics.map((topic, index) => (
                          <div 
                            key={index} 
                            className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center"
                          >
                            <span>{topic.theme}</span>
                            <span className="ml-2 bg-blue-200 px-2 rounded-full">{topic.count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </TabPanel>
              
              <TabPanel>
                {loading ? (
                  <Loader />
                ) : (
                  <TopComments comments={topComments} />
                )}
              </TabPanel>
              
              <TabPanel>
                {loading ? (
                  <Loader />
                ) : (
                  <DeveloperInsights insights={developerInsights} />
                )}
              </TabPanel>
            </Tabs>
          </div>
        )}
      </div>
      
      <footer className="mt-12 py-6 bg-gray-100 text-center text-gray-600">
        <p>GamePulse © {new Date().getFullYear()} - Community Feedback Analyzer</p>
      </footer>
    </div>
  );
}

export default App;