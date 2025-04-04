import { Grid, Card, CardContent, CardActionArea, Typography, Box } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import YouTubeIcon from '@mui/icons-material/YouTube'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import ImageIcon from '@mui/icons-material/Image'
import DescriptionIcon from '@mui/icons-material/Description'

interface Tool {
  title: string
  description: string
  path: string
  icon: JSX.Element
}

const tools: Tool[] = [
  {
    title: 'YouTube Downloader',
    description: 'Download videos and playlists from YouTube with ease',
    path: '/youtube-downloader',
    icon: <YouTubeIcon sx={{ fontSize: 40 }} />,
  },
  {
    title: 'Images to PDF',
    description: 'Convert multiple images into a single PDF document',
    path: '/images-to-pdf',
    icon: <PictureAsPdfIcon sx={{ fontSize: 40 }} />,
  },
  {
    title: 'PDF to Images',
    description: 'Extract images from PDF files or convert PDF pages to images',
    path: '/pdf-to-images',
    icon: <ImageIcon sx={{ fontSize: 40 }} />,
  },
  {
    title: 'Word to PDF',
    description: 'Convert Word documents to PDF format',
    path: '/word-to-pdf',
    icon: <DescriptionIcon sx={{ fontSize: 40 }} />,
  },
  {
    title: 'Image Converter',
    description: 'Convert images between different formats',
    path: '/image-converter',
    icon: <ImageIcon sx={{ fontSize: 40 }} />,
  },
]

const Home = () => {
  const navigate = useNavigate()

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h1" sx={{ mb: 4, textAlign: 'center' }}>
        Welcome to Tools Hub
      </Typography>
      <Typography variant="h2" sx={{ mb: 6, textAlign: 'center' }}>
        Your One-Stop Solution for File Conversions
      </Typography>
      <Grid container spacing={3}>
        {tools.map((tool) => (
          <Grid item xs={12} sm={6} md={4} key={tool.path}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: (theme) => theme.shadows[4],
                  transition: 'all 0.3s ease-in-out',
                },
              }}
            >
              <CardActionArea
                onClick={() => navigate(tool.path)}
                sx={{ height: '100%' }}
              >
                <CardContent
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    textAlign: 'center',
                    p: 3,
                  }}
                >
                  <Box
                    sx={{
                      mb: 2,
                      color: 'primary.main',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {tool.icon}
                  </Box>
                  <Typography
                    gutterBottom
                    variant="h5"
                    component="h2"
                    sx={{ mb: 2 }}
                  >
                    {tool.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {tool.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default Home