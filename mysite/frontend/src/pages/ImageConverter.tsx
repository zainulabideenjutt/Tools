import { useState, useCallback } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import ImageIcon from '@mui/icons-material/Image'
import DeleteIcon from '@mui/icons-material/Delete'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import axios from 'axios'

interface FileWithPreview extends File {
  preview?: string
}

const ImageConverter = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [targetFormat, setTargetFormat] = useState('png')
  const [convertedImages, setConvertedImages] = useState<string[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prevFiles) => [
      ...prevFiles,
      ...acceptedFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        })
      ),
    ])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'],
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setFiles((prevFiles) => {
      const newFiles = [...prevFiles]
      URL.revokeObjectURL(newFiles[index].preview || '')
      newFiles.splice(index, 1)
      return newFiles
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (files.length === 0) {
      setError('Please add at least one image')
      return
    }

    setError('')
    setSuccess(false)
    setLoading(true)

    const formData = new FormData()
    files.forEach((file) => {
      formData.append('original_images', file)
    })
    formData.append('convert_to', `.${targetFormat}`)

    try {
      const response = await axios.post('/api/image-converter', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Handle array of converted images
      const results = response.data
      if (Array.isArray(results) && results.length > 0) {
        const imageUrls = results.map((result: { converted_image: string }) => result.converted_image)
        setConvertedImages(imageUrls)
        setSuccess(true)
        setFiles([])
        

      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'An error occurred while processing your request'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{ py: 4 }}>
      <Typography variant="h1" sx={{ mb: 4, textAlign: 'center' }}>
        Image Converter
      </Typography>
      <Typography variant="h2" sx={{ mb: 6, textAlign: 'center' }}>
        Convert Images to Different Formats
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'grey.300',
              borderRadius: 1,
              p: 3,
              mb: 3,
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'primary.main',
              },
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Drop the images here'
                : 'Drag & drop images here, or click to select'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP
            </Typography>
          </Box>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Target Format</InputLabel>
                <Select
                  value={targetFormat}
                  label="Target Format"
                  onChange={(e) => setTargetFormat(e.target.value)}
                  disabled={loading}
                >
                  <MenuItem value="png">PNG</MenuItem>
                  <MenuItem value="jpg">JPG</MenuItem>
                  <MenuItem value="webp">WEBP</MenuItem>
                  <MenuItem value="gif">GIF</MenuItem>
                  <MenuItem value="bmp">BMP</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {files.length > 0 && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {files.map((file, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card>
                    <CardContent>
                      <img
                        src={file.preview}
                        alt={file.name}
                        style={{ width: '100%', height: 'auto', marginBottom: 2 }}
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle2" noWrap>{file.name}</Typography>
                          <Typography variant="body2" color="textSecondary">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </Typography>
                        </Box>
                        <IconButton
                          size="small"
                          onClick={() => removeFile(index)}
                          sx={{ ml: 1 }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}

          <Button
            variant="contained"
            fullWidth
            size="large"
            disabled={loading || files.length === 0}
            onClick={handleSubmit}
            sx={{ mt: 2 }}
          >
            {loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Convert Images'
            )}
          </Button>

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <AlertTitle>Success</AlertTitle>
              Your images have been converted successfully!
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <AlertTitle>Error</AlertTitle>
              {error}
            </Alert>
          )}
          {success && convertedImages.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h6" gutterBottom>
                Converted Images
              </Typography>
              <Grid container spacing={2}>
                {convertedImages.map((imageUrl, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <img
                          src={imageUrl}
                          alt={`Converted Image ${index + 1}`}
                          style={{ width: '100%', height: 'auto' }}
                        />
                        <Button
                          href={imageUrl}
                          download={`converted_image_${index + 1}.${targetFormat}`}
                          variant="outlined"
                          fullWidth
                          sx={{ mt: 1 }}
                        >
                          Download
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default ImageConverter