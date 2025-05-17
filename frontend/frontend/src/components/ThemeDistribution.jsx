import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

function ThemeDistribution({ data }) {
  // Convert the theme distribution object to an array for the chart
  const themeData = Object.entries(data).map(([theme, details]) => ({
    name: theme,
    value: details.count
  }));

  // Sort by value descending
  themeData.sort((a, b) => b.value - a.value);

  // Colors for the pie chart segments
  const COLORS = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a05195',
    '#d45087', '#f95d6a', '#ff7c43', '#ffa600', '#003f5c'
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const theme = payload[0].name;
      const count = payload[0].value;
      const percentage = data[theme]?.percentage || 0;
      
      return (
        <div className="bg-white p-3 border border-gray-200 rounded shadow-md">
          <p className="font-semibold">{theme}</p>
          <p>Count: {count}</p>
          <p>Percentage: {percentage.toFixed(1)}%</p>
        </div>
      );
    }
    return null;
  };

  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-gray-50 p-4 rounded-lg flex justify-center items-center h-64">
        <p className="text-gray-500">Theme distribution not available</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">Theme Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={themeData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
          >
            {themeData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend layout="vertical" align="right" verticalAlign="middle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ThemeDistribution;