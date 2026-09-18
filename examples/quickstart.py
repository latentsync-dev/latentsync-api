        """Minimal LatentSync example: create one prediction and print the output URL(s)."""
        import latentsync_api

        output = latentsync_api.run({
    "image_url": "https://example.com/input.png",
    "audio_url": "https://example.com/input.png"
})
        print(output)
