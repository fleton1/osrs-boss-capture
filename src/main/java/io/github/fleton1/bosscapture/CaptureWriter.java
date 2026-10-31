package io.github.fleton1.bosscapture;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;

/**
 * Appends one JSON object per line to a capture file. Serialisation happens on the
 * caller's thread (the client thread), disk writes on a private single thread.
 */
@Slf4j
class CaptureWriter implements AutoCloseable
{
	private final Gson gson;
	private final BufferedWriter out;
	private final ExecutorService io;
	@Getter
	private final Path path;

	CaptureWriter(Gson gson, Path path) throws IOException
	{
		this.gson = gson;
		this.path = path;
		Files.createDirectories(path.getParent());
		this.out = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
		this.io = Executors.newSingleThreadExecutor(r ->
		{
			Thread t = new Thread(r, "boss-capture-io");
			t.setDaemon(true);
			return t;
		});
	}

	void write(JsonObject line)
	{
		String json = gson.toJson(line);
		io.execute(() ->
		{
			try
			{
				out.write(json);
				out.write('\n');
			}
			catch (IOException e)
			{
				log.warn("capture write failed", e);
			}
		});
	}

	void flush()
	{
		io.execute(() ->
		{
			try
			{
				out.flush();
			}
			catch (IOException e)
			{
				log.warn("capture flush failed", e);
			}
		});
	}

	@Override
	public void close()
	{
		io.execute(() ->
		{
			try
			{
				out.close();
			}
			catch (IOException e)
			{
				log.warn("capture close failed", e);
			}
		});
		io.shutdown();
		try
		{
			io.awaitTermination(5, TimeUnit.SECONDS);
		}
		catch (InterruptedException e)
		{
			Thread.currentThread().interrupt();
		}
	}
}
