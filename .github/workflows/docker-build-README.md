# GitHub Actions Docker Build Workflow

This workflow automatically builds your Docker image using GitHub Actions.

## Features

- ✅ **Multi-platform builds**: Builds for both `linux/amd64` and `linux/arm64`
- ✅ **Automatic tagging**: Creates semantic version tags, branch tags, and SHA tags
- ✅ **GitHub Container Registry**: Pushes images to `ghcr.io` automatically
- ✅ **Build caching**: Uses GitHub Actions cache for faster builds
- ✅ **Pull request testing**: Builds (but doesn't push) on PRs
- ✅ **Manual triggers**: Can be triggered manually via workflow_dispatch

## Triggers

The workflow runs on:
- **Push to main/develop**: Builds and pushes with branch tags
- **Push tags (v*)**: Builds and pushes with version tags (e.g., v1.0.0)
- **Pull requests**: Builds only (doesn't push)
- **Manual dispatch**: Can be triggered manually from GitHub Actions UI

## Image Tags

The workflow creates multiple tags automatically:

- `latest` - Latest build from main branch
- `main` - Latest build from main branch
- `develop` - Latest build from develop branch
- `v1.0.0` - Semantic version tags (when you push a git tag)
- `v1.0` - Major.minor version
- `v1` - Major version only
- `main-abc1234` - Branch name + short commit SHA

## Using the Images

### Pull from GitHub Container Registry

```bash
# Pull latest
docker pull ghcr.io/YOUR_USERNAME/mcp-bear-notes:latest

# Pull specific version
docker pull ghcr.io/YOUR_USERNAME/mcp-bear-notes:v1.0.0

# Pull specific branch
docker pull ghcr.io/YOUR_USERNAME/mcp-bear-notes:main
```

### Update docker-compose.yml

Replace the build section with the pre-built image:

```yaml
services:
  mcp-bear-notes:
    image: ghcr.io/YOUR_USERNAME/mcp-bear-notes:latest
    # Remove the build section
    container_name: mcp-bear-notes
    # ... rest of config
```

## Setup Instructions

### 1. Enable GitHub Container Registry

The workflow uses GitHub's built-in `GITHUB_TOKEN`, so no additional secrets are needed for GHCR.

### 2. Make Repository Public or Configure Package Visibility

For private repositories, you may need to configure package visibility:
1. Go to your repository on GitHub
2. Navigate to Settings → Actions → General
3. Under "Workflow permissions", ensure "Read and write permissions" is selected

### 3. (Optional) Add Docker Hub Support

To also push to Docker Hub, uncomment the Docker Hub login section in the workflow and add these secrets:

1. Go to Settings → Secrets and variables → Actions
2. Add two secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

Then uncomment these lines in `.github/workflows/docker-build.yml`:

```yaml
- name: Log in to Docker Hub
  if: github.event_name != 'pull_request'
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

And update the metadata section to include Docker Hub:

```yaml
- name: Extract metadata (tags, labels)
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: |
      ghcr.io/${{ github.repository_owner }}/${{ env.IMAGE_NAME }}
      YOUR_DOCKERHUB_USERNAME/${{ env.IMAGE_NAME }}
```

## Creating Version Releases

To create a versioned release:

```bash
# Tag your commit
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push the tag
git push origin v1.0.0
```

This will trigger the workflow and create images with tags:
- `v1.0.0`
- `v1.0`
- `v1`

## Viewing Build Status

- Check the Actions tab in your GitHub repository
- Each workflow run shows:
  - Build logs
  - Build summary with all generated tags
  - Success/failure status

## Troubleshooting

### Build fails with permission errors

Ensure workflow permissions are set correctly:
1. Go to Settings → Actions → General
2. Under "Workflow permissions", select "Read and write permissions"
3. Check "Allow GitHub Actions to create and approve pull requests"

### Image not visible in packages

1. Go to your profile → Packages
2. Find the package
3. Click "Package settings"
4. Under "Danger Zone", change visibility if needed
5. Link the package to your repository

### Multi-platform build fails

The workflow builds for both amd64 and arm64. If you only need amd64:

```yaml
platforms: linux/amd64
```

## Best Practices

1. **Use semantic versioning**: Tag releases as `v1.0.0`, `v1.1.0`, etc.
2. **Test in PRs**: The workflow builds on PRs to catch issues early
3. **Use specific tags in production**: Don't use `latest` in production; use version tags
4. **Monitor build times**: Check Actions tab for build duration and optimize if needed

## Additional Resources

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Metadata Action](https://github.com/docker/metadata-action)