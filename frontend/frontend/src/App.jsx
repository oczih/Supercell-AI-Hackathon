import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css'
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import axios from 'axios';
import Loader from './components/Loader';
import WordCloud from './components/Wordcloud';
import ThemeDistribution from './components/ThemeDistribution';
import TopComments from './components/TopComments';
import DeveloperInsights from './components/DeveloperInsights';
import SettingsPanel from './components/SettingsPanel';


const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
console.log("API_URL:", API_URL);

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
    checkDataStatus();
  }, []);

  useEffect(() => {
    if (dataLoaded) {
      fetchAllData();
    }
  }, [dataSource, timePeriod, dataLoaded]);

  const checkDataStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/status`);
      const { posts_loaded, comments_loaded, analysis_loaded } = response.data;
      setDataLoaded(posts_loaded && comments_loaded && analysis_loaded);
      console.log(response.data);
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

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-sm">
          <p className="fw-semibold mb-1">{formatDate(label)}</p>
          <p>Sentiment: {payload[0].value.toFixed(2)}</p>
          <p>Comments: {payload[0].payload.count}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-vh-100 bg-light d-flex flex-column">
      <div className="container py-4 flex-grow-1">
        <header className="mb-5 text-center">
          <h1 className="display-4 fw-bold text-dark">GamePulse</h1>
          <p className="lead text-secondary">Real-Time Community Feedback Analyzer</p>
        </header>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {!dataLoaded ? (
          <SettingsPanel onLoadData={loadData} loading={loading} />
        ) : (
          <div className="bg-white rounded shadow p-4">
            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
              <div className="d-flex gap-2">
                <select
                  value={dataSource}
                  onChange={(e) => setDataSource(e.target.value)}
                  className="form-select"
                  style={{ minWidth: '150px' }}
                >
                  <option value="reddit">Reddit</option>
                  <option value="youtube" disabled>YouTube (Coming Soon)</option>
                  <option value="app_store" disabled>App Store (Coming Soon)</option>
                </select>

                <select
                  value={timePeriod}
                  onChange={(e) => setTimePeriod(e.target.value)}
                  className="form-select"
                  style={{ minWidth: '150px' }}
                >
                  <option value="day">Hourly</option>
                  <option value="hour">Daily</option>
                  <option value="week">Weekly</option>
                </select>
              </div>

              <button
                onClick={fetchAllData}
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </button>
            </div>

            <Tabs selectedIndex={activeTab} onSelect={(index) => setActiveTab(index)}>
              <TabList className="nav nav-tabs mb-4">
                <Tab className="nav-link" selectedClassName="active" style={{ cursor: 'pointer' }}>Dashboard</Tab>
                <Tab className="nav-link" selectedClassName="active" style={{ cursor: 'pointer' }}>Comments</Tab>
                <Tab className="nav-link" selectedClassName="active" style={{ cursor: 'pointer' }}>Developer Mode</Tab>
              </TabList>

              <TabPanel>
                {loading ? (
                  <Loader />
                ) : (
                  <div className="row gy-4">
                    {/* Sentiment Over Time Chart */}
                    <div className="col-12 col-lg-6 bg-light rounded p-3">
                      <h2 className="h5 fw-semibold mb-3">Sentiment Over Time</h2>
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
                            stroke="#0d6efd" /* Bootstrap primary blue */
                            activeDot={{ r: 8 }}
                            name="Sentiment Score"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Theme Distribution */}
                    <div className="col-12 col-lg-6">
                      <ThemeDistribution data={themeDistribution} />
                    </div>

                    {/* Word Cloud */}
                    <div className="col-12 col-lg-6">
                      <WordCloud imageUrl={wordcloudImage} />
                    </div>

                    {/* Trending Topics */}
                    <div className="col-12 col-lg-6 bg-light rounded p-3">
                      <h2 className="h5 fw-semibold mb-3">Trending Words/Topics</h2>
                      <div className="d-flex flex-wrap gap-2">
                        {trendingTopics.map((topic, index) => (
                          <span
                            key={index}
                            className="badge bg-primary d-flex align-items-center"
                            style={{ gap: '0.5rem' }}
                          >
                            {topic.theme}
                            <span className="badge bg-white text-primary rounded-pill px-2">
                              {topic.count}
                            </span>
                          </span>
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

      <footer className="py-3 bg-light text-center text-secondary">
        <p className="mb-0">GamePulse © {new Date().getFullYear()} - Community Feedback Analyzer</p>
      </footer>
    </div>
  );
}

export default App;
