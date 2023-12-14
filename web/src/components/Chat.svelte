<script lang="ts">
  let text = "";
  const chat = (prompt: string) => {
    const es = new EventSource(
      `http://127.0.0.1:8000/api/stream/sse?prompt=${prompt}`,
      {}
    );

    es.onopen = (event) => {
      text = "";
      console.log(es.readyState, event.type);
    };
    es.onmessage = (event) => {
      text += event.data;
      console.log(es.readyState, "message:", event.data);
    };
    es.onerror = (event) => {
      console.log(es.readyState, "error:", event);
    };
    es.addEventListener("end", (event) => {
      es.close();
      console.log(es.readyState, event.type);
    });
  };

  // https://stackoverflow.com/questions/40385133/retrieve-data-from-a-readablestream-object
  export async function streamToText(
    stream: ReadableStream<Uint8Array>
  ): Promise<string> {
    let result = "";
    const reader = stream.pipeThrough(new TextDecoderStream()).getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      console.log(value);

      result += value;
    }
    console.log(result);

    return result;
  }

  const jsonStream = async () => {
    const response = await fetch("http://127.0.0.1:8000/api/stream/json");
    if (!response.body) {
      return;
    }
    streamToText(response.body);
  };

  const ndjsonStream = async () => {
    const response = await fetch("http://127.0.0.1:8000/api/stream/ndjson");
    if (!response.body) {
      return;
    }
    streamToText(response.body);
  };
</script>

<button
  on:click={() => {
    chat("你好");
  }}
>
  你好
</button>

<section>
  {text}
</section>

<button on:click={jsonStream}>jsonStream</button>
<button on:click={ndjsonStream}>ndjsonStream</button>
