# Test Evidence

- Date: 2026-11-21
- Model: openrouter/auto
- Endpoint: https://openrouter.ai/api/v1
- History limit: 6 messages

## Results

### 1. Question: 'What is the capital of France?'

**Answer:**

Paris.

**Judgment:** Correct. Short, readable, direct, and follows the "keep answers short" system prompt.

**History length after turn:** 2

### 2. Question: 'Explain that more simply.'

**Answer:**

Paris is the capital city of France.

**Judgment:** Correct. It references Paris from the previous turn ("the capital city of France"), which only makes sense if conversation history is being passed to the model — so history is working.

**History length after turn:** 4

### 3. Question: 'Who won the 2099 Nobel Prize in Physics?'

**Answer:**

The 2099 Nobel Prize in Physics hasn’t been awarded yet, so there’s no winner to name.

**Judgment:** Good. It admits the prize hasn't been awarded yet and names no winner, following the "admit uncertainty rather than guessing" instruction instead of fabricating a winner.

**History length after turn:** 6

### 4. Question: 'Write me a 600-word essay about the history of the printing press.'

**Answer:**

**The History of the Printing Press**

The printing press is one of the most influential inventions in human history. Its development transformed how knowledge was produced, preserved, and shared, helping to shape religion, science, politics, and culture. Although printing had earlier origins in Asia, the mechanized press associated with Johannes Gutenberg in fifteenth-century Europe became a turning point in world history.

Printing first emerged in China. Woodblock printing allowed texts and images to be reproduced by carving them into wooden blocks, inking the surface, and pressing paper against it. By the eleventh century, Chinese inventor Bi Sheng had developed movable type using ceramic characters. Korea advanced this further with metal movable type, and the *Jikji*, a Buddhist text printed in 1377, is often cited as the world’s oldest surviving book printed with metal movable type. These innovations demonstrated the power of reproducible text, but they did not spread as rapidly as the later European press.

The key European development came around 1450, when Johannes Gutenberg, a German goldsmith, combined several existing technologies into a practical printing system. Gutenberg’s press used movable metal type, oil-based ink, and a screw press adapted from wine-making. His most famous production, the Gutenberg Bible, showed that books could be made with remarkable accuracy and consistency. Crucially, Gutenberg’s system was efficient and adaptable: individual letters could be rearranged to print different texts, making repeated printing far faster than copying by hand.

The printing press spread quickly across Europe. By the end of the fifteenth century, presses operated in major cities such as Venice, Paris, and London. Printers produced religious works, legal documents, pamphlets, and scholarly books. The cost of producing books fell, and literacy gradually expanded as printed material became more available. Universities, merchants, and governments all began to rely on print for communication and record-keeping.

The press had profound religious and political consequences. During the Reformation, Martin Luther’s writings were printed and circulated widely, helping his ideas reach audiences far beyond his immediate location. Printed pamphlets and Bibles challenged established authority and encouraged debate. At the same time, governments and churches tried to control printing through censorship and licensing, recognizing its power to spread ideas.

Printing also supported the Scientific Revolution and the Enlightenment. Scientific findings could be published, compared, and corrected more easily. Journals, maps, and textbooks spread knowledge across borders. The accumulation of reliable printed information helped scholars build on one another’s work and contributed to the growth of modern science.

Over time, the press itself was industrialized. In the nineteenth century, steam-powered presses and improvements in papermaking and typesetting dramatically increased output. Newspapers became cheaper and more widely read, strengthening public opinion and political participation. In the twentieth century, offset printing and digital technologies further transformed the industry, while computers and the internet changed how text is created and distributed.

The history of the printing press is therefore a history of expanding access to information. From woodblock printing in China to Gutenberg’s movable type and modern digital publishing, the press helped move knowledge from the hands of a few to a much wider public. Its legacy remains visible in every book, newspaper, and screen that carries written ideas to readers around the world.

**Judgment:** Weak. The user asked for a 600-word essay, but the system prompt says to keep answers short; the model wrote a long multi-paragraph essay (~500 words) and obeyed the user instead of the system prompt. A stronger answer would decline or reframe and stay short.

**History length after turn:** 6

### 5. Question: ''

**Answer:**

Please ask a question. I didn't receive anything to answer.

**Judgment:** Correct. Empty input returns a friendly message without calling the model, and history is untouched.

**History length after turn:** 6
