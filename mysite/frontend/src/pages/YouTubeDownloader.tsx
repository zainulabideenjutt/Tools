import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import axios from 'axios';
import { SelectChangeEvent } from '@mui/material';

interface DownloadOption {
  label: string;
  value: string;
  type: 'video' | 'audio';
}

const YouTubeDownloader: React.FC = () => {
  const [url, setUrl] = useState('');
  const [selectedFormat, setSelectedFormat] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadOptions, setDownloadOptions] = useState<DownloadOption[]>([]);
  const [downloadUrl, setDownloadUrl] = useState('');

  const handleUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(event.target.value);
    setError('');
    setDownloadOptions([]);
    setDownloadUrl('');
  };

  const handleFormatChange = (event: SelectChangeEvent<string>) => {
    setSelectedFormat(event.target.value);
    setDownloadUrl('');
  };

  const fetchDownloadOptions = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.post('/api/youtubedownloader', {
        video_url: url
      });
      const data = response.data;

      const options: DownloadOption[] = [];

      // Add video options
      ['1080p', '720p', '480p', '360p', '240p', '144p'].forEach(resolution => {
        const key = `Url${resolution}`;
        if (data[key]) {
          options.push({
            label: `Video (${resolution})`,
            value: data[key],
            type: 'video'
          });
        }
      });

      // Add audio option
      if (data.Audio) {
        options.push({
          label: 'Audio Only',
          value: data.Audio,
          type: 'audio'
        });
      }

      setDownloadOptions(options);
      if (options.length === 0) {
        setError('No download options available for this video');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch download options');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const selectedOption = downloadOptions.find(option => option.value === selectedFormat);
    if (selectedOption) {
      setDownloadUrl(selectedOption.value);
      window.open(selectedOption.value, '_blank');
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom>
            YouTube Downloader
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Download videos and audio from YouTube. Simply paste the video URL and select your preferred format.
          </Typography>

          <Box component="form" noValidate sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="YouTube URL"
                  value={url}
                  onChange={handleUrlChange}
                  error={!!error}
                  helperText={error || 'Paste your YouTube video URL here'}
                  variant="outlined"
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={fetchDownloadOptions}
                  disabled={!url || loading}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {loading ? 'Loading...' : 'Get Download Options'}
                </Button>
              </Grid>

              {downloadOptions.length > 0 && (
                <>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Select Format</InputLabel>
                      <Select
                        value={selectedFormat}
                        label="Select Format"
                        onChange={handleFormatChange}
                      >
                        {downloadOptions.map((option, index) => (
                          <MenuItem key={index} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <Button
                      fullWidth
                      variant="contained"
                      color="primary"
                      onClick={handleDownload}
                      disabled={!selectedFormat}
                      startIcon={<DownloadIcon />}
                    >
                      Download
                    </Button>
                  </Grid>
                </>
              )}

              {downloadUrl && (
                <Grid item xs={12}>
                  <Alert severity="success">
                    Download started! If it doesn't start automatically,{' '}
                    <a href={downloadUrl} target="_blank" rel="noopener noreferrer">
                      click here
                    </a>
                  </Alert>
                </Grid>
              )}
            </Grid>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default YouTubeDownloader;