import { Box, Container } from '@mui/material'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import YouTubeDownloader from './pages/YouTubeDownloader'
import ImagesToPDF from './pages/ImagesToPDF'
import PDFToImages from './pages/PDFToImages'
import WordToPDF from './pages/WordToPDF'
import ImageConverter from './pages/ImageConverter'

const App = () => {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/youtube-downloader" element={<YouTubeDownloader />} />
          <Route path="/images-to-pdf" element={<ImagesToPDF />} />
          <Route path="/pdf-to-images" element={<PDFToImages />} />
          <Route path="/word-to-pdf" element={<WordToPDF />} />
          <Route path="/image-converter" element={<ImageConverter />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App