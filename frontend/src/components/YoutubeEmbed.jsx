export default function YoutubeEmbed({ videoId }) {
  return (
    <div className="youtube-wrapper">
      <iframe
        className="youtube-iframe"
        src={`https://www.youtube.com/embed/${videoId}?rel=0`}
        title="YouTube video player"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
  )
}
