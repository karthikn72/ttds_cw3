from google.cloud import storage
import pandas as pd
from transformers import T5Tokenizer
from torch.utils.data import DataLoader
from t5_dataset import T5Dataset
from t5_finetuner import T5FineTuner
from tqdm.auto import tqdm
import os
import argparse
import torch

class CategoryPredictor():
    def __init__(self, class_name) -> None:
        self.model = None
        self.class_name = class_name
        self.keyfile_path = 'src/tools/sentinews-413116-89709afcbbd7.json'
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base', model_max_length=512, truncation=True)

    def load_model(self):
        if not os.path.exists('categories_model'):
            storage_client = storage.Client.from_service_account_json(self.keyfile_path)
            
            bucket = storage_client.get_bucket('sentinews-articles')

            blob = bucket.get_blob('cat_model_t')

            print("Downloading pretrained model from cloud")

            with open('categories_model', 'wb') as f:
                with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                    storage_client.download_blob_to_file(blob, file_obj)

        arg_dict = dict(
            model_name_or_path='t5-base',
            tokenizer_name_or_path='t5-base',
            max_seq_length=512,
            learning_rate=1e-4,
            weight_decay=0.0,
            adam_epsilon=1e-8,
            warmup_steps=0,
            train_batch_size=8,
            eval_batch_size=8,
            num_train_epochs=12,
            gradient_accumulation_steps=16,
            n_gpu=1,
            early_stop_callback=True,
            opt_level='O1',
            max_grad_norm=1.0,
            seed=42,
        )

        self.model = T5FineTuner(argparse.Namespace(**arg_dict), self.class_name)

        self.model.load_state_dict(torch.load('categories_model'))

        print("The model has been loaded successfully")


    def predict(self, text_df) -> str:
        def take_substring_until_char(input_string, target_char):
            index = input_string.find(target_char)
            if index != -1:
                substring = input_string[:index]
                return substring
            else:
                return input_string
        
        dataset = T5Dataset(self.class_name, self.tokenizer, text_df) 
        loader = DataLoader(dataset, batch_size=16, shuffle=False)
        self.model.model.eval()
        outputs = []
        for batch in loader:
            outs = self.model.model.generate(input_ids=batch['source_ids'], 
                                    attention_mask=batch['source_mask'], 
                                    max_length=8)
            
            # dec = [take_substring_until_char(self.tokenizer.decode(ids)[5:].strip(), '<') for ids in outs]
            dec = [ids for ids in outs]
            
            outputs.extend(dec)

        return list(map(lambda x: take_substring_until_char(self.tokenizer.decode(x)[5:].strip(), '<'), outputs))

    

if __name__ == '__main__':
    pred = CategoryPredictor('category')
    pred.load_model()
    

    sent1 = """The Revolutionary Street Art Project That Inspired Banksy And Empowered A City's Youth\nJohn Nation just wanted to give teenagers in Bristol, southwest England, a safe place to spray-paint without fear of arrest and prosecution. Little did the then 21-year-old youth worker know back in 1984 that his “Aerosol Art Project” at the Barton Hill Youth Center would go some way to shaping British and global street art over the coming years and decades. It spawned an entire generation of influential and genre-defining artists ― including Banksy. But as Nation, now 54, told HuffPost in a wide-ranging interview, the initiative also almost ended up costing him his job, his reputation and his liberty. Nation was just 18-years-old when, in 1981, he became an outreach worker at the youth center in his home neighborhood of Barton Hill. “We helped kids deal with the nitty gritty of life [...] providing sexual health awareness, talking about drugs, that kind of thing,” he told HuffPost. A trip to Amsterdam\xa0in 1982 sparked an interest in graffiti, which he saw adorning the Dutch capital’s streets. “I started reading whatever material I could.” Coincidentally, some of the 14 to 19-year-olds attending the center were also becoming interested in the art form. Inspired by movies such as “Wild Style” and “Beat Street” and the painting of Bristol’s earliest-recognized graffiti artist 3D (a.k.a. Robert Del Naja from Massive Attack), Nation said they’d spend hours copying outlines of the work featured in the seminal book “Subway Art.” When one teen returned from New York City with photographs of the graffiti he’d seen, Nation allowed the teen and his friends to paint the club’s front wall. “Barton Hill was rough,” Nation said. “At that time the club was very territorial, seen as right wing, predominantly white and very hostile to outsiders.” Its exterior walls, he said, were mainly daubed with anti-authority slogans such as “No Police State in Barton Hill” or ones promoting the far-right movement, the National Front. “These guys produced a piece that was so vibrant,” Nation said. “It helped break down some barriers. Lots of these guys listened to hip hop, reggae and black-inspired music. Lots of the artists they looked up to were black, hispanic and Puerto Rican, but they were in a predominantly white area. Being involved in graffiti opened their eyes and helped to lower their prejudices.” Inspired by what the teens had produced, Nation sought permission from his employers at the now-defunct Avon County Council authority to set up the “Barton Hill Aerosol Art Project” — a place he envisioned would let the youngsters, some of whom were only a bit younger than him, to “express themselves freely and legally” on the center’s walls instead of tagging or painting unauthorized spots on public or private property which could lead to their arrest. Cheo\xa0and\xa0Inkie\xa0were among the first generation of budding street artists to attend the center, which had the added appeal of being the only one in the city with an indoor skate ramp. Before long, the artists covered most of the building with their work. “Once word got out that it was a safe environment to paint and look at books and photographs and watch films about graffiti, then people from across the city started coming,” Nation said. “Once you had that one group of people give it their seal of approval, others saw it was safe and followed suit.” At its peak, more than 40 youngsters regularly attended the project. Graffiti writers from across the U.K. also visited, and it inspired other authorities from around the country to launch similar initiatives.  “It was a great atmosphere, very expressive, very creative,” Nation added. “There was never any bad vibes or competition, none of that element. It was all about being a crew and a togetherness and I still think that’s true to all the guys who still know each other and paint now.” Not everyone was in favor of the project, however. Unbeknownst to Nation, from 1988 to 1989 the British Transport Police surveilled the center and several of its artists as part of a city-wide investigation into graffiti tagging and criminal behavior. John Nation Operation Anderson\xa0sought to profile graffiti artists suspected of criminal damage and culminated with a series of raids on properties across the region. Police arrested dozens of people, including Nation. Officers searched his home and the center. “Bearing in mind that I was running an aerosol art project, there was no way there wasn’t going to be any material at the center,” he said. “It was like an Aladdin’s Cave for them.” Police seized a “massive stash of paint” Nation had procured from the project’s sponsors and his treasured 5,000-plus snaps of graffiti he’d either taken himself or been sent by writers from around the world.  Nation believes police thought the club was “some kind of ‘Axis of Evil’ that was the main meeting point for all of Bristol’s illegal graffiti writers and a place where other writers from across the country would come.”  “It wasn’t that at all though,” he said, although he acknowledges some of the artists were painting on unauthorized spots on their own.\xa0 As was revealed in the BBC documentary “Drawing The Line,” (above), police matched tags on the artwork in the club to tags on illegal works across the city.  They charged several artists with criminal damage. Nation himself was charged with suspicion of conspiracy to incite individuals to commit criminal damage.  “Their main case against me was that the photos and books I had, if shown to a young person of impressional age, would incite them to go out and commit criminal damage,”\xa0Nation said. “They also said I was covering up for the young people and I was duty bound to divulge information on them. But I didn’t assist them whatsoever. I answered ‘no comment’ to pretty much everything.” Several artists were found guilty of criminal damage and received fines. Nation’s charge, however, was dropped on the day his trial was due to begin after prosecutors offered no evidence of incitement.\xa0 A post shared by John Nation (@johnnation) on Jun 1, 2017 at 8:53am PDT Nation says he then consciously used the subsequent press coverage to promote his project’s work and to argue that without a place to legally paint, “the illegal culture of the art form just gets reinforced.” Following the police raids, Nation says many of those involved in the city’s street art scene went “underground for a while.” “It was like they were regrouping,” he said. “Many of the guys arrested took a break, lessened their illegal activities, and some decided painting legally was the only way.” Nation says the publicity did inspire, however, a new generation of artists to begin visiting the project ― with one of them being Banksy. “As a young boy, he’d come to the center and watch people paint. He was heavily into hip hop culture, graffiti, and Barton Hill was where it was happening. Every weekend there was fresh work going up on the walls and people would exchange ideas,” Nation said.  “He says he called it his religious pilgrimage every weekend to go. Many of these guys had their own crazy, little dreams and he said what Barton Hill showed him was very powerful, that you could go on to follow those dreams.” At that time, Nation says Banksy (who despite multiple attempts and theories has never been officially identified), wasn’t producing the political or social commentary pieces that he’s since become globally famous for.  As part of a crew with some slightly older teens, Nation says he was “into graffiti and letterforms and writing.” He also didn’t stand out “as one of the graffiti writers you’d call a ‘top boy,’” nor was he using his “Banksy” moniker either, says Nation. “The Banksy thing came later.” Nation claims Banksy is “without doubt” the biggest contemporary artist in the world right now, but admits he didn’t foresee his rise to prominence during his early days of painting at the center. Instead, he believes Banksy truly began to make his mark when he changed his style and began using stencils. “Not only could he paint quicker, he could paint more locations and produce more work. He started off with quite crude stencil work, like the rats, then he started progressing to more clean work, more sharper,” Nation said. “These smaller stencils started appearing across the city and for me, it’s once he made that conscious decision to change the style of what he was painting and the content of what he was painting when he exploded,” he added. Banksy himself admits in his book “Wall and Piece” that his switch in style came when aged 18 transport police chased him through a thorny bush after spotting him painting “LATE AGAIN” on the side of a train. “The rest of my mates made it to the car and disappeared so I spent over an hour hidden under a dumper truck with engine oil leaking all over me,” he wrote. “As I lay there listening to the cops on the tracks I realized I had to cut my painting time in half or give up altogether. I was staring straight up at the stenciled plate on the bottom of a fuel tank when I realized I could just copy that style and make each letter three feet high.” Nation said that change led Banksy to “strike an accord with first and foremost the Bristol public, and then the British public.” “Lots of people who wouldn’t be into street art could relate to the simplicity and the fun and the characters he was painting. As he’s become more mature, the images and message have become more hard-hitting — he’s a clever guy.”\xa0 A post shared by Banksy (@banksy) on May 7, 2017 at 6:40am PDT Nation does question how Banksy creates some of his works, such as the “Brexit” piece (above) that he unveiled in Dover, southeast England, in May as a commentary on the U.K.’s referendum vote to leave the European Union. “Yes he painted it, but he’s got to have a team of people that set up the scaffold and he must have approached the people who own the property before that,” Nation said. “You can’t just rock up and set up a scaffold on the side of someone’s property without there being no questions asked. It’s a huge wall. It’s massive.” With so much history between Nation and Banksy, one may assume the pair remain close and in touch. When faced with the suggestion, however, Nation responded with a stony silence before changing the subject. While the legacy of the Barton Hill Youth Center often focuses on Banksy, many of the center’s other alum have also gone on to enjoy hugely successful careers.\xa0Jody Thomas, who in April gave HuffPost a helping hand in unveiling its new logo (below), has painted and exhibited his signature photo-realistic style around the world: But for him, it also all began at the center, which he first attended when he was just 15 years old after being encouraged by a school friend who’d described Nation to him as “outspoken, politically militant and not one to suffer fools.”  “It felt like I was being led to meet the leader of a despotic cult,” Thomas told HuffPost, adding that Nation “didn’t disappoint” when he finally met him.  “He immediately went through my school folder of work based around the comic art of 2,000 A.D. and classical painting and drawings,” he said. “I think he saw in me the opportunity to add a different artistic dimension to the club’s repertoire and left me to recreate on the walls of the club what I had on paper.” Jody Thomas Thomas credits Nation as being at “the forefront” of the street art movement at that time. “His energy and personality has garnered him an amount of respect amongst Bristolians on the level of any rock star or public figure,” he said. “For me, he is the ‘Darwin’ of street art in the U.K. and gave me a opportunity to express the art that spoke to me all those years ago.” The admiration is mutual. Nation still remembers the day that Thomas first brought in his work which was “totally different” to what was being produced in the club at the time. “I thought to myself, ‘fucking hell, this is amazing. He’s 15 and painting like this?’ I thought, ‘this boy is going to go far,’” Nation said. “At first he wasn’t accepted as much by the graffiti lads. Jody was into indie music and a lot of that music had dark imagery on its album sleeves,” he added. “He embraced that kind of artwork. He painted small pieces, then he painted these two black and white heads (below) and that was it. I have a lot of time for him. He didn’t stick to what everyone else was doing. He just wanted to be an artist and express his talents.” Inkie, a.k.a. Tom Bingle, also emerged from the center. He’s since worked as a head of design at SEGA and hosted his own shows across the globe.\xa0Recently, he painted alongside Shepard Fairey, the artist behind the\xa0“Hope” poster\xa0that came to define former President Barack Obama’s 2008 campaign. For Inkie, Nation’s project acted as a vital “central hub” for the city’s graffiti artists in the pre-internet era of the late ‘80s to mid-90s. “Without this center and John’s support of our artwork, Bristol would not have had the scene it maintains today,” he told HuffPost. By 1991, however, Nation had become disillusioned with the restraints he felt the authority was putting on him and quit. “I was seen as being quite outspoken, left wing and a bit of a socialist,” he said. “But I’m proud of what I did back then. And the fact that people still talk about then and what I achieved for me is justification for what I did do.” Nation went on to forge a successful career in promoting dance music events across the U.K. and the NASS action sports and music show in Somerset.  With the explosion in the popularity of street art, which he puts principally down to the rise of the internet and social media, he’s since come full circle ― and now gives regular tours of Bristol’s scene via the WhereTheWall tour. “People from all over the world come, and no one tour is the same. Street art is here today, gone tomorrow. The art form is transient,” he said. In April, Nation curated his first ever solo show, “Graffiti Nation,” at Bristol’s Upfest gallery, the home of\xa0Europe’s largest live street art festival. He also worked with Inkie on the “See No Evil” art exhibition in 2011 and 2012, and remains a fierce advocate for spaces where artists can legally paint. He’s also set to feature in another BBC documentary, which will analyze the U.K. street art scene in the decades since Operation Anderson. Nation’s pedigree, knowledge and influence of street art and the genres that umbrella term encompasses have seen him nicknamed the “Godfather” of the Bristol (and increasingly British) scene. But it’s a label\xa0that doesn’t sit well with him. “I look back and I feel that all those years ago I was vilified and I could have possibly lost my job,” he said. “Then two years ago I’m being used as the face of Bristol tourism as someone who represents it as a progressive, cultural city. Who would have thought it?” “I get called the ‘Godfather,’ but I’m not. I just had a faith and a belief in these young people when no one else would give them the time of day,” he added. “I’m just lucky enough that i’ve been involved in the graffiti scene and seen it emerge. Bristol is not what it is because of me, far from it. I’m just one cog in the wheel, just like Banksy and all the others.” Check out John Nation’s Instagram, Facebook and the tour website for\xa0WhereTheWall.
    """  
    sent2 = """'Tomb Raider Games Group Embracer Raises $182 Million in Share Issue\nSTOCKHOLM (Reuters) - Embattled gaming group Embracer has raised 2 billion crowns ($182 million) in a share issue directed to institutional investors, it said in a statement on Thursday.\n\nThe Swedish group said in a statement it had issued 80,000 new shares at a subscription price of 25 crowns per share.\n\nEmbracer last month launched a programme to slash investments and costs, having been hit by development delays, weaker demand, bad reception for some new games and the fall-through of a planned strategic partnership.\n\n"The proceeds from this share issue will further strengthen our financial position, improving both financing cost and our operational flexibility, and enabling us to focus on the key aspects of the program," it said on Thursday.\n\nEmbracer, which last year bought several development studios and the intellectual property rights to a number of games including a new Tomb Raider game, had announced the plans for the share issue late on Wednesday.'
"""

    sent3 = """Thousands Evacuated as Fire Hits Warehouse in Crowded Hong Kong District
HONG KONG (Reuters) - Hong Kong firefighters battled to control a blaze at a warehouse in the city's bustling Kowloon district on Friday, with smoke billowing out from windows and engulfing the white square building.

Authorities said no casualties have been reported so far as they upgraded the fire to Number 3 from Number 1 at 2 p.m. (0600 GMT). Number 5 is the highest rating, followed by a Disaster Alert.

Cable Television said two nearby schools needed to be evacuated."""
    df = pd.DataFrame(columns=['text'])
    new_row1 = {'text': sent1}
    new_row2 = {'text': sent2}
    new_row3 = {'text': sent3}
    ls = [sent1, sent2, sent3]
    ls2 = []
    for i in range(3):
        content = ls[i]
        ls2.append(content)
    # df = pd.concat([df, pd.DataFrame([new_row1])], ignore_index=True)
    # df = pd.concat([df, pd.DataFrame([new_row2])], ignore_index=True)
    # df = pd.concat([df, pd.DataFrame([new_row3])], ignore_index=True)
    
    df['text'] = df['text'].tolist() + ls2

    df2 = pd.DataFrame(columns = ['id'])
    df2['id'] = df2['id'].tolist() + [1,2,3]
    ans = pred.predict(df)
    print(ans)
    print(df)
    print(df2)
    print(pd.concat([df['text'], df2['id']], axis=1))