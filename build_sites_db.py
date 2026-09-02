"""
build_sites_db.py
------------------
Gera o arquivo responsa/data/sites.json com a base de sites usados na
busca por nome de usuário (username). Cada entrada define:

  - id: identificador interno
  - name: nome de exibição
  - url: template da URL de perfil (usa {} no lugar do username)
  - category: "social" (rede social) ou "general" (demais sites)
  - method: método de verificação ("status_code" é o padrão -> 200 =
            encontrado, 404 = não encontrado, outros códigos = indefinido)

IMPORTANTE: sites mudam de layout com frequência. Esta base é um ponto
de partida (arquitetura no estilo Sherlock/WhatsMyName) e deve ser
revisada/atualizada pela comunidade ao longo do tempo. Isso fica
documentado no README.
"""
import json

SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/{}/"),
    ("twitter_x", "Twitter / X", "https://x.com/{}"),
    ("facebook", "Facebook", "https://www.facebook.com/{}"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@{}"),
    ("youtube", "YouTube", "https://www.youtube.com/@{}"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/{}"),
    ("reddit", "Reddit", "https://www.reddit.com/user/{}"),
    ("pinterest", "Pinterest", "https://www.pinterest.com/{}"),
    ("twitch", "Twitch", "https://www.twitch.tv/{}"),
    ("github", "GitHub", "https://github.com/{}"),
    ("gitlab", "GitLab", "https://gitlab.com/{}"),
    ("telegram", "Telegram", "https://t.me/{}"),
    ("vk", "VKontakte", "https://vk.com/{}"),
    ("tumblr", "Tumblr", "https://{}.tumblr.com"),
    ("medium", "Medium", "https://medium.com/@{}"),
    ("flickr", "Flickr", "https://www.flickr.com/people/{}"),
    ("vimeo", "Vimeo", "https://vimeo.com/{}"),
    ("soundcloud", "SoundCloud", "https://soundcloud.com/{}"),
    ("spotify", "Spotify", "https://open.spotify.com/user/{}"),
    ("snapchat", "Snapchat", "https://www.snapchat.com/add/{}"),
    ("steam", "Steam", "https://steamcommunity.com/id/{}"),
    ("threads", "Threads", "https://www.threads.net/@{}"),
    ("mastodon", "Mastodon (mastodon.social)", "https://mastodon.social/@{}"),
    ("kwai", "Kwai", "https://www.kwai.com/@{}"),
    ("behance", "Behance", "https://www.behance.net/{}"),
    ("dribbble", "Dribbble", "https://dribbble.com/{}"),
    ("myspace", "Myspace", "https://myspace.com/{}"),
    ("vsco", "VSCO", "https://vsco.co/{}"),
]

GENERAL = [
    ("hackernews", "Hacker News", "https://news.ycombinator.com/user?id={}"),
    ("producthunt", "Product Hunt", "https://www.producthunt.com/@{}"),
    ("kaggle", "Kaggle", "https://www.kaggle.com/{}"),
    ("codepen", "CodePen", "https://codepen.io/{}"),
    ("replit", "Replit", "https://replit.com/@{}"),
    ("dockerhub", "Docker Hub", "https://hub.docker.com/u/{}"),
    ("npm", "npm", "https://www.npmjs.com/~{}"),
    ("pypi", "PyPI", "https://pypi.org/user/{}"),
    ("devto", "DEV Community", "https://dev.to/{}"),
    ("hashnode", "Hashnode", "https://hashnode.com/@{}"),
    ("sourceforge", "SourceForge", "https://sourceforge.net/u/{}/"),
    ("bitbucket", "Bitbucket", "https://bitbucket.org/{}/"),
    ("keybase", "Keybase", "https://keybase.io/{}"),
    ("aboutme", "About.me", "https://about.me/{}"),
    ("gravatar", "Gravatar", "https://en.gravatar.com/{}"),
    ("wordpress", "WordPress.com", "https://{}.wordpress.com"),
    ("blogger", "Blogger", "https://{}.blogspot.com"),
    ("quora", "Quora", "https://www.quora.com/profile/{}"),
    ("slideshare", "SlideShare", "https://www.slideshare.net/{}"),
    ("scribd", "Scribd", "https://www.scribd.com/{}"),
    ("trello", "Trello", "https://trello.com/{}"),
    ("freecodecamp", "freeCodeCamp", "https://www.freecodecamp.org/{}"),
    ("codeforces", "Codeforces", "https://codeforces.com/profile/{}"),
    ("leetcode", "LeetCode", "https://leetcode.com/{}"),
    ("hackerrank", "HackerRank", "https://www.hackerrank.com/{}"),
    ("itch_io", "itch.io", "https://{}.itch.io"),
    ("bandcamp", "Bandcamp", "https://{}.bandcamp.com"),
    ("mixcloud", "Mixcloud", "https://www.mixcloud.com/{}"),
    ("discogs", "Discogs", "https://www.discogs.com/user/{}"),
    ("genius", "Genius", "https://genius.com/{}"),
    ("lastfm", "Last.fm", "https://www.last.fm/user/{}"),
    ("letterboxd", "Letterboxd", "https://letterboxd.com/{}"),
    ("myanimelist", "MyAnimeList", "https://myanimelist.net/profile/{}"),
    ("deviantart", "DeviantArt", "https://www.deviantart.com/{}"),
    ("px500", "500px", "https://500px.com/p/{}"),
    ("unsplash", "Unsplash", "https://unsplash.com/@{}"),
    ("patreon", "Patreon", "https://www.patreon.com/{}"),
    ("kofi", "Ko-fi", "https://ko-fi.com/{}"),
    ("etsy", "Etsy", "https://www.etsy.com/shop/{}"),
    ("ebay", "eBay", "https://www.ebay.com/usr/{}"),
    ("chesscom", "Chess.com", "https://www.chess.com/member/{}"),
    ("lichess", "Lichess", "https://lichess.org/@/{}"),
    ("trakt", "Trakt", "https://trakt.tv/users/{}"),
    ("wellfound", "Wellfound (AngelList)", "https://wellfound.com/u/{}"),
    ("goodreads", "Goodreads", "https://www.goodreads.com/{}"),
    ("fiverr", "Fiverr", "https://www.fiverr.com/{}"),
    ("researchgate", "ResearchGate", "https://www.researchgate.net/profile/{}"),
    ("academia_edu", "Academia.edu", "https://independent.academia.edu/{}"),
    ("disqus", "Disqus", "https://disqus.com/by/{}"),
    ("imgur", "Imgur", "https://imgur.com/user/{}"),
    ("giphy", "GIPHY", "https://giphy.com/{}"),
    ("ifunny", "iFunny", "https://ifunny.co/user/{}"),
    ("wattpad", "Wattpad", "https://www.wattpad.com/user/{}"),
    ("ao3", "Archive of Our Own", "https://archiveofourown.org/users/{}"),
    ("codewars", "Codewars", "https://www.codewars.com/users/{}"),
    ("gumroad", "Gumroad", "https://{}.gumroad.com"),
    ("buymeacoffee", "Buy Me a Coffee", "https://www.buymeacoffee.com/{}"),
    ("houzz", "Houzz", "https://www.houzz.com/user/{}"),
    ("foursquare", "Foursquare", "https://foursquare.com/{}"),
    ("weheartit", "We Heart It", "https://weheartit.com/{}"),
    ("ravelry", "Ravelry", "https://www.ravelry.com/people/{}"),
    ("namemc", "NameMC (Minecraft)", "https://namemc.com/profile/{}"),
    ("osu", "osu!", "https://osu.ppy.sh/users/{}"),
    ("speedrun", "Speedrun.com", "https://www.speedrun.com/user/{}"),
    ("ello", "Ello", "https://ello.co/{}"),
    ("newgrounds", "Newgrounds", "https://{}.newgrounds.com"),
    ("carbonmade", "Carbonmade", "https://{}.carbonmade.com"),
    ("issuu", "Issuu", "https://issuu.com/{}"),
    ("gitee", "Gitee", "https://gitee.com/{}"),
    ("launchpad", "Launchpad", "https://launchpad.net/~{}"),
    ("sketchfab", "Sketchfab", "https://sketchfab.com/{}"),
    ("opensea", "OpenSea", "https://opensea.io/{}"),
    ("rarible", "Rarible", "https://rarible.com/{}"),
    ("pastebin", "Pastebin", "https://pastebin.com/u/{}"),
    ("crates_io", "crates.io", "https://crates.io/users/{}"),
    ("indiehackers", "Indie Hackers", "https://www.indiehackers.com/{}"),
    ("f6s", "F6S", "https://www.f6s.com/{}"),
    ("polywork", "Polywork", "https://www.polywork.com/{}"),
    ("peerlist", "Peerlist", "https://peerlist.io/{}"),
    ("write_as", "Write.as", "https://{}.write.as"),
    ("substack", "Substack", "https://{}.substack.com"),
    ("microblog", "Micro.blog", "https://micro.blog/{}"),
    ("pixelfed", "Pixelfed", "https://pixelfed.social/{}"),
    ("minds", "Minds", "https://www.minds.com/{}"),
    ("askfm", "ASKfm", "https://ask.fm/{}"),
    ("linktree", "Linktree", "https://linktr.ee/{}"),
    ("carrd", "Carrd", "https://{}.carrd.co"),
    ("beacons", "Beacons", "https://beacons.ai/{}"),
    ("mshake", "msha.ke", "https://msha.ke/{}"),
    ("taplink", "Taplink", "https://taplink.cc/{}"),
    ("redbubble", "Redbubble", "https://www.redbubble.com/people/{}"),
    ("society6", "Society6", "https://society6.com/{}"),
    ("teepublic", "TeePublic", "https://www.teepublic.com/user/{}"),
    ("zazzle", "Zazzle", "https://www.zazzle.com/{}"),
    ("rubygems", "RubyGems", "https://rubygems.org/profiles/{}"),
    ("9gag", "9GAG", "https://9gag.com/u/{}"),
    ("mercadolivre", "Mercado Livre (BR)", "https://www.mercadolivre.com.br/perfil/{}"),
    ("elo7", "Elo7 (BR)", "https://www.elo7.com.br/loja/{}"),
    ("catarse", "Catarse (BR)", "https://www.catarse.me/{}"),
    ("hackaday", "Hackaday.io", "https://hackaday.io/{}"),
    ("opencollective", "Open Collective", "https://opencollective.com/{}"),
]

def main():
    entries = []
    for sid, name, url in SOCIAL:
        entries.append({
            "id": sid, "name": name, "url": url,
            "category": "social", "method": "status_code",
        })
    for sid, name, url in GENERAL:
        entries.append({
            "id": sid, "name": name, "url": url,
            "category": "general", "method": "status_code",
        })

    out = {
        "meta": {
            "total": len(entries),
            "social_count": len(SOCIAL),
            "general_count": len(GENERAL),
        },
        "sites": entries,
    }

    with open("responsa/data/sites.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Gerado sites.json com {len(entries)} sites "
          f"({len(SOCIAL)} redes sociais + {len(GENERAL)} sites gerais)")

if __name__ == "__main__":
    main()
