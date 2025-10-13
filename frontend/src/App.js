import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Box, AppBar, Toolbar, Typography, Paper, Button, TextField, Grid, Avatar,
  Card, CardContent, Collapse, IconButton, Tooltip, InputAdornment
} from "@mui/material";
import CloudIcon from '@mui/icons-material/Cloud';
import SearchIcon from '@mui/icons-material/Search';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';

const BACKEND = "http://localhost:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [weather, setWeather] = useState(null);
  const [history, setHistory] = useState([]);
  const [expanded, setExpanded] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

   
  useEffect(() => {
    document.body.style.background = "linear-gradient(120deg, #e7eaf5 0%, #f1f5fa 100%)";
  }, []);

  // Load weather record history
  useEffect(() => {
    axios.get(`${BACKEND}/weather`).then(res => setHistory(res.data)).catch(() => {});
  }, []);

  // Submit new query
  const handleSubmit = async () => {
    setError("");
    if (!query || !dateFrom || !dateTo) {
      setError("Please fill all fields: Location, Start date, and End date.");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${BACKEND}/weather/`, null, {
        params: { query, date_from: dateFrom, date_to: dateTo }
      });
      setWeather(res.data);
      setHistory(prev => [res.data, ...prev]);
      setExpanded(e => ({ ...e, [res.data.id]: true }));
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
        "Sorry, we couldn't find the weather for that place and time."
      );
    }
    setLoading(false);
  };

  // Export CSV
  const handleExport = async () => {
    const res = await axios.get(`${BACKEND}/export/?format=csv`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute("download", "weather-data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Delete record
  const handleDelete = async id => {
    await axios.delete(`${BACKEND}/weather/${id}`);
    setHistory(history.filter(r => r.id !== id));
    if (weather?.id === id) setWeather(null);
  };

  // Card toggle
  const handleExpand = id => setExpanded(exp => ({ ...exp, [id]: !exp[id] }));

  return (
    <Box>
      {/* Top bar, Perplexity style */}
      <AppBar position="static" sx={{ background: "#fff", boxShadow: "none", borderBottom: "1.5px solid #eaeaea" }}>
        <Toolbar>
          <CloudIcon sx={{ color: "#6166dc", fontSize: 32, mr: 2 }} />
          <Typography variant="h6" sx={{ color: "#23263b", fontWeight: 900, letterSpacing: 1 }}>weatherperplex</Typography>
        </Toolbar>
      </AppBar>

      {/* Main content card */}
      <Grid container justifyContent="center">
        <Grid item xs={12} sm={10} md={7} lg={6}>
          <Paper elevation={3} sx={{ borderRadius: 4, p: 4, mt: 6, mb: 2, background: "#fff8", minHeight: 370 }}>
            <Typography variant="h4" sx={{ color: "#6166dc", fontWeight: 900, mb: 1 }}>
              Your Weather AI
            </Typography>
            <Typography sx={{ mb: 3, color: "#23263b" }}>
              Enter a location, date range, then click Get Weather like you would <b>in a Perplexity.com chat</b>.
            </Typography>
            <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
              <TextField
                variant="outlined"
                label="Place / City / Landmark"
                value={query}
                onChange={e => setQuery(e.target.value)}
                sx={{ flex: 2 }}
                InputProps={{
                  endAdornment: <InputAdornment position="end"><SearchIcon /></InputAdornment>
                }}
              />
              <TextField
                label="From"
                type="date"
                value={dateFrom}
                onChange={e => setDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ width: 120 }}
              />
              <TextField
                label="To"
                type="date"
                value={dateTo}
                onChange={e => setDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
                sx={{ width: 120 }}
              />
              <Button variant="contained" disabled={loading} sx={{
                borderRadius: 3, fontWeight: 700, background: "linear-gradient(90deg, #6166dc, #2169bf)"
              }} onClick={handleSubmit}>
                Get Weather
              </Button>
              <Tooltip title="Export as CSV">
                <span>
                  <IconButton onClick={handleExport} size="large">
                    <DownloadIcon sx={{ color: "#6166dc" }} />
                  </IconButton>
                </span>
              </Tooltip>
            </Box>
            {error &&
              <Typography sx={{
                background: "#ffc9c9", color: "#b71c1c", fontWeight: 900,
                borderRadius: 2, p: 1.1, mb: 1.8, fontSize: 19, mt: 1
              }}>{error}</Typography>
            }
            {/* Result */}
            {weather && (
              <Card elevation={6} sx={{
                mt: 2, mb: 2, borderRadius: 4, px: 3, background: "#f1f6fe", py: 1, borderLeft: "9px solid #6166dc"
              }}>
                <CardContent>
                  <Typography variant="h5" sx={{ color: "#2e2f4b", fontWeight: 900, letterSpacing: 0.9 }}>{weather.location}</Typography>
                  <Typography sx={{ mb: 1, color: "#6166dc", fontWeight: 500 }}>
                    {weather.date_from} to {weather.date_to}
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 1.5 }}>
                    <Avatar src="https://www.svgrepo.com/show/530993/cloud-sun.svg" alt="weather icon" sx={{ width: 46, height: 46 }} />
                    <Typography sx={{ fontSize: 22, color: "#1a1a2e" }}>
                      <b>{weather.temperature} °C</b>
                    </Typography>
                    <Typography sx={{ ml: 3, color: "#23263b" }}>{weather.details}</Typography>
                  </Box>
                  {weather.map_url &&
                    <Box sx={{ mt: 2 }}>
                      <iframe title="map"
                        width="100%"
                        height="180"
                        style={{ borderRadius: 12, border: "1px solid #eee" }}
                        src={weather.map_url}
                        allowFullScreen />
                    </Box>}
                  {weather.youtube_url &&
                    <Box sx={{ mt: 2 }}>
                      <a href={weather.youtube_url} target="_blank" rel="noopener noreferrer"
                        style={{ textDecoration: "none", color: "#196edc", fontWeight: 700 }}>
                        See Weather Videos for This Place (YouTube)
                      </a>
                    </Box>}
                </CardContent>
              </Card>
            )}
          </Paper>

          {/* History of weather queries */}
          {history.length > 0 &&
            <Paper elevation={2} sx={{ borderRadius: 3, mt: 3, background: "#fafaff", p: 2.3 }}>
              <Typography variant="h6" sx={{ color: "#6166dc", mb: 1, fontWeight: 900 }}>
                Previous Queries
              </Typography>
              {history.map(rec =>
                <Card key={rec.id} sx={{
                  borderRadius: 3, my: 1.3, boxShadow: "0 2px 10px #6166dc17",
                  background: "#fff", borderLeft: "5px solid #6166dc"
                }}>
                  <CardContent sx={{ py: 1.6 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <Typography sx={{ fontWeight: 700 }}>
                        {rec.location} — {rec.date_from} to {rec.date_to} : {rec.temperature}°C
                      </Typography>
                      <IconButton aria-label="delete" onClick={() => handleDelete(rec.id)}>
                        <DeleteIcon sx={{ color: "#6166dc" }} />
                      </IconButton>
                    </Box>
                    <Collapse in={expanded[rec.id]}>
                      <Box sx={{ mt: 1 }}>
                        <div style={{ fontSize: 14, color: "#2e2f4b" }}>{rec.details}</div>
                        {rec.map_url && (
                          <iframe title="map"
                            width="100%"
                            height="110"
                            style={{ borderRadius: 9, border: "1px solid #eee", marginTop: 8 }}
                            src={rec.map_url}
                            allowFullScreen />
                        )}
                        {rec.youtube_url &&
                          <Box><a href={rec.youtube_url} target="_blank" rel="noopener noreferrer" style={{ color: "#196edc" }}>
                            Youtube videos
                          </a></Box>}
                      </Box>
                    </Collapse>
                    <Button
                      onClick={() => handleExpand(rec.id)}
                      sx={{ mt: 1, color: "#6166dc" }}
                      size="small">{expanded[rec.id] ? "Hide details" : "Show details"}</Button>
                  </CardContent>
                </Card>
              )}
            </Paper>}
        </Grid>
      </Grid>
    </Box>
  );
}
