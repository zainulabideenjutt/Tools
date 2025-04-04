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
} from '@mui/material'
import { useDropzone } from 'react-dropzone'
import ImageIcon from '@mui/icons-material/Image'
import DeleteIcon from '@mui/icons-material/Delete'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import axios from 'axios'

interface FileWithPreview extends File {
  preview?: string
}

const ImagesToPDF = () => {
  const [files, setFiles] = useState<FileWithPreview[]>([])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')

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
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
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
      formData.append('images', file)
    })

    try {
      const response = await axios.post('/api/images-to-pdf-converter', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setDownloadUrl(response.data.converted_pdf)
      setSuccess(true)
      setFiles([])
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
        Images to PDF Converter
      </Typography>
      <Typography variant="h2" sx={{ mb: 6, textAlign: 'center' }}>
        Convert Your Images to PDF
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
              Supported formats: PNG, JPG, JPEG, GIF, BMP
            </Typography>
          </Box>

          {files.length > 0 && (
            <List>
              {files.map((file, index) => (
                <ListItem
                  key={file.name}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => removeFile(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemIcon>
                    <ImageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                </ListItem>
              ))}
            </List>
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
              'Convert to PDF'
            )}
          </Button>

          {success && downloadUrl && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                <AlertTitle>Success</AlertTitle>
                Your images have been converted to PDF successfully!
              </Alert>
              <Button
                variant="contained"
                fullWidth
                size="large"
                href={downloadUrl}
                download
                sx={{ mt: 2 }}
              >
                Download PDF
              </Button>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <AlertTitle>Error</AlertTitle>
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default ImagesToPDF