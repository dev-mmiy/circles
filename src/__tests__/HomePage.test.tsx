/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import HomePage from '../app/[locale]/page'

// Mock next-intl
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string, params?: any) => {
    const translations: Record<string, string> = {
      'header.title': 'Healthcare Community',
      'header.newPost': 'New Post',
      'header.refreshPosts': 'Refresh Posts',
      'welcome.title': 'Welcome to Healthcare Community',
      'welcome.subtitle': 'A platform for supporting people with serious illnesses',
      'posts.title': 'Community Posts',
      'posts.noPosts': 'No posts found',
      'posts.tryAgain': 'Try Again',
      'posts.createNew': 'Create New Post',
      'posts.form.title': 'Title',
      'posts.form.titlePlaceholder': 'Enter post title',
      'posts.form.content': 'Content',
      'posts.form.contentPlaceholder': 'Share your thoughts...',
      'posts.form.creating': 'Creating...',
      'posts.form.createPost': 'Create Post',
      'posts.postedOn': 'Posted on {date}',
      'api.status': 'API Connection Status',
      'api.loading': 'Loading posts from API...',
      'api.connected': 'Successfully connected to API',
      'api.foundPosts': 'Found {count} posts',
      'api.error': 'Failed to load posts from API',
      'api.errorHint': 'Make sure the backend API is running on port 8001',
      'api.createError': 'Failed to create post',
      'common.loading': 'Loading...',
      'common.cancel': 'Cancel'
    }
    return params ? translations[key]?.replace('{count}', params.count)?.replace('{date}', params.date) || key : translations[key] || key
  },
  useLocale: () => 'en-US'
}))

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn()
  })
}))

// Mock fetch
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>

describe('HomePage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the main title', () => {
    render(<HomePage />)
    expect(screen.getByText('Healthcare Community')).toBeInTheDocument()
  })

  it('renders welcome message', () => {
    render(<HomePage />)
    expect(screen.getByText('Welcome to Healthcare Community')).toBeInTheDocument()
    expect(screen.getByText('A platform for supporting people with serious illnesses')).toBeInTheDocument()
  })

  it('shows language switcher buttons', () => {
    render(<HomePage />)
    expect(screen.getByText('EN')).toBeInTheDocument()
    expect(screen.getByText('日本語')).toBeInTheDocument()
    expect(screen.getByText('FR')).toBeInTheDocument()
  })

  it('shows new post and refresh buttons', () => {
    render(<HomePage />)
    expect(screen.getByText('New Post')).toBeInTheDocument()
    expect(screen.getByText('Refresh Posts')).toBeInTheDocument()
  })

  it('shows create post form when new post button is clicked', () => {
    render(<HomePage />)
    
    const newPostButton = screen.getByText('New Post')
    fireEvent.click(newPostButton)
    
    expect(screen.getByText('Create New Post')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter post title')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Share your thoughts...')).toBeInTheDocument()
  })

  it('hides create post form when cancel is clicked', () => {
    render(<HomePage />)
    
    // Open form
    const newPostButton = screen.getByText('New Post')
    fireEvent.click(newPostButton)
    
    // Close form - use getAllByText to get the form cancel button specifically
    const cancelButtons = screen.getAllByText('Cancel')
    const formCancelButton = cancelButtons.find(button => 
      button.getAttribute('type') === 'button'
    )
    fireEvent.click(formCancelButton)
    
    expect(screen.queryByText('Create New Post')).not.toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    render(<HomePage />)
    expect(screen.getByText('Loading posts from API...')).toBeInTheDocument()
  })

  it('handles API error state', async () => {
    (global.fetch as jest.MockedFunction<typeof fetch>).mockRejectedValueOnce(new Error('API Error'))
    
    render(<HomePage />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load posts from API')).toBeInTheDocument()
    })
  })

  it('displays posts when API returns data', async () => {
    const mockPosts = [
      {
        id: 1,
        title: 'Test Post',
        content: 'Test content',
        group_id: 1,
        created_at: '2025-09-27T12:00:00Z'
      }
    ]
    
    // Mock fetch to return the posts
    (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockPosts)
      } as Response)
    )
    
    render(<HomePage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test Post')).toBeInTheDocument()
      expect(screen.getByText('Test content')).toBeInTheDocument()
    })
  })

  it('shows no posts message when API returns empty array', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })
    
    render(<HomePage />)
    
    await waitFor(() => {
      expect(screen.getByText('No posts found')).toBeInTheDocument()
    })
  })

  it('creates a new post successfully', async () => {
    const mockNewPost = {
      id: 1,
      title: 'New Test Post',
      content: 'New test content',
      group_id: 1,
      created_at: '2025-09-27T12:00:00Z'
    }
    
    // Mock initial posts fetch
    (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      } as Response)
    )
    
    // Mock post creation
    (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockNewPost)
      } as Response)
    )
    
    render(<HomePage />)
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('No posts found')).toBeInTheDocument()
    })
    
    // Open create form
    const newPostButton = screen.getByText('New Post')
    fireEvent.click(newPostButton)
    
    // Fill form
    const titleInput = screen.getByPlaceholderText('Enter post title')
    const contentInput = screen.getByPlaceholderText('Share your thoughts...')
    
    fireEvent.change(titleInput, { target: { value: 'New Test Post' } })
    fireEvent.change(contentInput, { target: { value: 'New test content' } })
    
    // Submit form
    const createButton = screen.getByText('Create Post')
    fireEvent.click(createButton)
    
    await waitFor(() => {
      expect(screen.getByText('New Test Post')).toBeInTheDocument()
    })
  })

  it('handles post creation error', async () => {
    // Mock initial posts fetch
    (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      } as Response)
    )
    
    // Mock post creation error
    (global.fetch as jest.MockedFunction<typeof fetch>).mockImplementationOnce(() =>
      Promise.reject(new Error('Creation failed'))
    )
    
    render(<HomePage />)
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('No posts found')).toBeInTheDocument()
    })
    
    // Open create form
    const newPostButton = screen.getByText('New Post')
    fireEvent.click(newPostButton)
    
    // Fill and submit form
    const titleInput = screen.getByPlaceholderText('Enter post title')
    fireEvent.change(titleInput, { target: { value: 'Test' } })
    
    const createButton = screen.getByText('Create Post')
    fireEvent.click(createButton)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to create post')).toBeInTheDocument()
    })
  })
})
