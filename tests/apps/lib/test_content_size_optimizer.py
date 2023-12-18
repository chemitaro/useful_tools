from apps.lib.content_size_optimizer import ContentSizeOptimizer
from apps.lib.utils import count_tokens


class TestContentSizeOptimizer:
    contents = [
        "App Router | Next.js Menu Using App Router Features available in /app App Router The Next.js App Router is a new paradigm for building applications using React's latest features. If you're already familiar with Next.js, you'll find that the App Router is a natural evolution of the existing file-system based router in the Pages Router . For new applications, we recommend using the App Router . For existing applications, you can incrementally adopt the App Router . It's also possible to use both routers in the same application. Frequently Asked Questions How can I access the request object in a layout? You intentionally cannot access the raw request object. However, you can access headers and cookies through server-only functions. You can also set cookies . Layouts do not rerender. They can be cached and reused to avoid unnecessary computation when navigating between pages. By restricting layouts from accessing the raw request, Next.js can prevent the execution of potentially slow or expensive user code within the layout, which could negatively impact performance. This design also enforces consistent and predictable behavior for layouts across different pages, simplify development and debugging since developers can rely on layouts behaving the same way regardless of the specific page they are applied to. Depending on the UI pattern you're building, Parallel Routes allow you to render multiple pages in the same layout, and pages have access to the route segments as well as the URL search params. How can I access the URL on a page? By default, pages are Server Components. You can access the route segments through the params prop and the URL search params through the searchParams prop for a given page. If you are using Client Components, you can use usePathname , useSelectedLayoutSegment , and useSelectedLayoutSegments for more complex routes. Further, depending on the UI pattern you're building, Parallel Routes allow you to render multiple pages in the same layout, and pages have access to the route segments as well as the URL search params. How can I redirect from a Server Component? You can use redirect to redirect from a page to a relative or absolute URL. redirect is a temporary (307) redirect, while permanentRedirect is a permanent (308) redirect. When these functions are used while streaming UI, they will insert a meta tag to emit the redirect on the client side. How can I handle authentication with the App Router? Here are some common authentication solutions that support the App Router: NextAuth.js Clerk Auth0 Stytch Kinde Or manually handling sessions or JWTs How can I set cookies? You can set cookies in Server Actions or Route Handlers using the cookies function. Since HTTP does not allow setting cookies after streaming starts, you cannot set cookies from a page or layout directly. You can also set cookies from Middleware . How can I build multi-tenant apps? If you are looking to build a single Next.js application that serves multiple tenants, we have built an example showing our recommended architecture. How can I invalidate the App Router cache? There are multiple layers of caching in Next.js, and thus, multiple ways to invalidate different parts of the cache. Learn more about caching . Are there any comprehensive, open-source applications built on the App Router? Yes. You can view Next.js Commerce or the Platforms Starter Kit for two larger examples of using the App Router that are open-source. Learn More Routing Fundamentals Data Fetching, Caching, and Revalidating Forms and Mutations Caching Rendering Fundamentals Server Components Client Components Building Your Application Learn how to use Next.js features to build your application. API Reference Next.js API Reference for the App Router. Was this helpful? supported. Send",  # noqa: E501
        "App Router: API Reference | Next.js Menu Using App Router Features available in /app App Router API Reference API Reference The Next.js API reference is divided into the following sections: Components API Reference for Next.js built-in components. File Conventions API Reference for Next.js Special Files. Functions API Reference for Next.js Functions and Hooks. next.config.js Options Learn how to configure your application with next.config.js. create-next-app Create Next.js apps in one command with create-next-app. Edge Runtime API Reference for the Edge Runtime. Next.js CLI The Next.js CLI allows you to start, build, and export your application. Learn more about it here. Was this helpful? supported. Send",  # noqa: E501
        "API Reference: Components | Next.js Menu Using App Router Features available in /app App Router API Reference Components Components Font Optimizing loading web fonts with the built-in `next/font` loaders. <Image> Optimize Images in your Next.js Application using the built-in `next/image` Component. <Link> Enable fast client-side navigation with the built-in `next/link` component. <Script> Optimize third-party scripts in your Next.js application using the built-in `next/script` Component. Was this helpful? supported. Send",  # noqa: E501
        "Components: Font | Next.js Menu Using App Router Features available in /app App Router ... Components Font Font Module This API reference will help you understand how to use next/font/google and next/font/local . For features and usage, please see the Optimizing Fonts page. Font Function Arguments For usage, review Google Fonts and Local Fonts . Key font/google font/local Type Required src String or Array of Objects Yes weight String or Array Required/Optional style String or Array - subsets Array of Strings - axes Array of Strings - display String - preload Boolean - fallback Array of Strings - adjustFontFallback Boolean or String - variable String - declarations Array of Objects - src The path of the font file as a string or an array of objects (with type Array<path: string, weight?: string, style?: string> ) relative to the directory where the font loader function is called. Used in next/font/local Required Examples: src:'./fonts/my-font.woff2' where my-font.woff2 is placed in a directory named fonts inside the app directory src:[{path: './inter/Inter-Thin.ttf', weight: '100',},{path: './inter/Inter-Regular.ttf',weight: '400',},{path: './inter/Inter-Bold-Italic.ttf', weight: '700',style: 'italic',},] if the font loader function is called in app/page.tsx using src:'../styles/fonts/my-font.ttf' , then my-font.ttf is placed in styles/fonts at the root of the project weight The font weight with the following possibilities: A string with possible values of the weights available for the specific font or a range of values if it's a variable font An array of weight values if the font is not a variable google font . It applies to next/font/google only. Used in next/font/google and next/font/local Required if the font being used is not variable Examples: weight: '400' : A string for a single weight value - for the font Inter , the possible values are '100' , '200' , '300' , '400' , '500' , '600' , '700' , '800' , '900' or 'variable' where 'variable' is the default) weight: '100 900' : A string for the range between 100 and 900 for a variable font weight: ['100','400','900'] : An array of 3 possible values for a non variable font style The font style with the following possibilities: A string value with default value of 'normal' An array of style values if the font is not a variable google font . It applies to next/font/google only. Used in next/font/google and next/font/local Optional Examples: style: 'italic' : A string - it can be normal or italic for next/font/google style: 'oblique' : A string - it can take any value for next/font/local but is expected to come from standard font styles style: ['italic','normal'] : An array of 2 values for next/font/google - the values are from normal and italic subsets The font subsets defined by an array of string values with the names of each subset you would like to be preloaded . Fonts specified via subsets will have a link preload tag injected into the head when the preload option is true, which is the default. Used in next/font/google Optional Examples: subsets: ['latin'] : An array with the subset latin You can find a list of all subsets on the Google Fonts page for your font. axes Some variable fonts have extra axes that can be included. By default, only the font weight is included to keep the file size down. The possible values of axes depend on the specific font. Used in next/font/google Optional Examples: axes: ['slnt'] : An array with value slnt for the Inter variable font which has slnt as additional axes as shown here . You can find the possible axes values for your font by using the filter on the Google variable fonts page and looking for axes other than wght display The font display with possible string values of 'auto' , 'block' , 'swap' , 'fallback' or 'optional' with default value of 'swap' . Used in next/font/google and next/font/local Optional Examples: display: 'optional' : A string assigned to the optional value preload A boolean value that specifies whether the font should be preloaded or not. The default is true . Used in next/font/google and next/font/local Optional Examples: preload: false fallback The fallback font to use if the font cannot be loaded. An array of strings of fallback fonts with no default. Optional Used in next/font/google and next/font/local Examples: fallback: ['system-ui', 'arial'] : An array setting the fallback fonts to system-ui or arial adjustFontFallback For next/font/google : A boolean value that sets whether an automatic fallback font should be used to reduce Cumulative Layout Shift . The default is true . For next/font/local : A string or boolean false value that sets whether an automatic fallback font should be used to reduce Cumulative Layout Shift . The possible values are 'Arial' , 'Times New Roman' or false . The default is 'Arial' . Used in next/font/google and next/font/local Optional Examples: adjustFontFallback: false : for next/font/google adjustFontFallback: 'Times New Roman' : for next/font/local variable A string value to define the CSS variable name to be used if the style is applied with the CSS variable method . Used in next/font/google and next/font/local Optional Examples: variable: '--my-font' : The CSS variable --my-font is declared declarations An array of font face descriptor key-value pairs that define the generated @font-face further. Used in next/font/local Optional Examples: declarations: [{ prop: 'ascent-override', value: '90%' }] Applying Styles You can apply the font styles in three ways: className style CSS Variables className Returns a read-only CSS className for the loaded font to be passed to an HTML element. < p className = { inter .className}>Hello, Next.js!</ p > style Returns a read-only CSS style object for the loaded font to be passed to an HTML element, including style.fontFamily to access the font family name and fallback fonts. < p style = { inter .style}>Hello World</ p > CSS Variables If you would like to set your styles in an external style sheet and specify additional options there, use the CSS variable method. In addition to importing the font, also import the CSS file where the CSS variable is defined and set the variable option of the font loader object as follows: app/page.tsx import { Inter } from 'next/font/google' import styles from '../styles/component.module.css' const inter = Inter ({ variable : '--font-inter' , }) To use the font, set the className of the parent container of the text you would like to style to the font loader's variable value and the className of the text to the styles property from the external CSS file. app/page.tsx < main className = { inter .variable}> < p className = { styles .text}>Hello World</ p > </ main > Define the text selector class in the component.module.css CSS file as follows: styles/component.module.css .text { font-family : var (--font-inter) ; font-weight : 200 ; font-style : italic ; } In the example above, the text Hello World is styled using the Inter font and the generated font fallback with font-weight: 200 and font-style: italic . Using a font definitions file Every time you call the localFont or Google font function, that font will be hosted as one instance in your application. Therefore, if you need to use the same font in multiple places, you should load it in one place and import the related font object where you need it. This is done using a font definitions file. For example, create a fonts.ts file in a styles folder at the root of your app directory. Then, specify your font definitions as follows: styles/fonts.ts import { Inter , Lora , Source_Sans_3 } from 'next/font/google' import localFont from 'next/font/local' // define your variable fonts const inter = Inter () const lora = Lora () // define 2 weights of a non-variable font const sourceCodePro400 = Source_Sans_3 ({ weight : '400' }) const sourceCodePro700 = Source_Sans_3 ({ weight : '700' }) // define a custom local font where GreatVibes-Regular.ttf is stored in the styles folder const greatVibes = localFont ({ src : './GreatVibes-Regular.ttf' }) export { inter , lora , sourceCodePro400 , sourceCodePro700 , greatVibes } You can now use these definitions in your code as follows: app/page.tsx import { inter , lora , sourceCodePro700 , greatVibes } from '../styles/fonts' export default function Page () { return ( < div > < p className = { inter .className}>Hello world using Inter font</ p > < p style = { lora .style}>Hello world using Lora font</ p > < p className = { sourceCodePro700 .className}> Hello world using Source_Sans_3 font with weight 700 </ p > < p className = { greatVibes .className}>My title in Great Vibes font</ p > </ div > ) } To make it easier to access the font definitions in your code, you can define a path alias in your tsconfig.json or jsconfig.json files as follows: tsconfig.json",  # noqa: E501
        "App Router | Next.js Menu Using App Router Features available in /app App Router The Next.js App Router is a new paradigm for building applications using React's latest features. If you're already familiar with Next.js, you'll find that the App Router is a natural evolution of the existing file-system based router in the Pages Router . For new applications, we recommend using the App Router . For existing applications, you can incrementally adopt the App Router . It's also possible to use both routers in the same application. Frequently Asked Questions How can I access the request object in a layout? You intentionally cannot access the raw request object. However, you can access headers and cookies through server-only functions. You can also set cookies . Layouts do not rerender. They can be cached and reused to avoid unnecessary computation when navigating between pages. By restricting layouts from accessing the raw request, Next.js can prevent the execution of potentially slow or expensive user code within the layout, which could negatively impact performance. This design also enforces consistent and predictable behavior for layouts across different pages, simplify development and debugging since developers can rely on layouts behaving the same way regardless of the specific page they are applied to. Depending on the UI pattern you're building, Parallel Routes allow you to render multiple pages in the same layout, and pages have access to the route segments as well as the URL search params. How can I access the URL on a page? By default, pages are Server Components. You can access the route segments through the params prop and the URL search params through the searchParams prop for a given page. If you are using Client Components, you can use usePathname , useSelectedLayoutSegment , and useSelectedLayoutSegments for more complex routes. Further, depending on the UI pattern you're building, Parallel Routes allow you to render multiple pages in the same layout, and pages have access to the route segments as well as the URL search params. How can I redirect from a Server Component? You can use redirect to redirect from a page to a relative or absolute URL. redirect is a temporary (307) redirect, while permanentRedirect is a permanent (308) redirect. When these functions are used while streaming UI, they will insert a meta tag to emit the redirect on the client side. How can I handle authentication with the App Router? Here are some common authentication solutions that support the App Router: NextAuth.js Clerk Auth0 Stytch Kinde Or manually handling sessions or JWTs How can I set cookies? You can set cookies in Server Actions or Route Handlers using the cookies function. Since HTTP does not allow setting cookies after streaming starts, you cannot set cookies from a page or layout directly. You can also set cookies from Middleware . How can I build multi-tenant apps? If you are looking to build a single Next.js application that serves multiple tenants, we have built an example showing our recommended architecture. How can I invalidate the App Router cache? There are multiple layers of caching in Next.js, and thus, multiple ways to invalidate different parts of the cache. Learn more about caching . Are there any comprehensive, open-source applications built on the App Router? Yes. You can view Next.js Commerce or the Platforms Starter Kit for two larger examples of using the App Router that are open-source. Learn More Routing Fundamentals Data Fetching, Caching, and Revalidating Forms and Mutations Caching Rendering Fundamentals Server Components Client Components Building Your Application Learn how to use Next.js features to build your application. API Reference Next.js API Reference for the App Router. Was this helpful? supported. Send",  # noqa: E501
        "App Router: API Reference | Next.js Menu Using App Router Features available in /app App Router API Reference API Reference The Next.js API reference is divided into the following sections: Components API Reference for Next.js built-in components. File Conventions API Reference for Next.js Special Files. Functions API Reference for Next.js Functions and Hooks. next.config.js Options Learn how to configure your application with next.config.js. create-next-app Create Next.js apps in one command with create-next-app. Edge Runtime API Reference for the Edge Runtime. Next.js CLI The Next.js CLI allows you to start, build, and export your application. Learn more about it here. Was this helpful? supported. Send",  # noqa: E501
        "API Reference: Components | Next.js Menu Using App Router Features available in /app App Router API Reference Components Components Font Optimizing loading web fonts with the built-in `next/font` loaders. <Image> Optimize Images in your Next.js Application using the built-in `next/image` Component. <Link> Enable fast client-side navigation with the built-in `next/link` component. <Script> Optimize third-party scripts in your Next.js application using the built-in `next/script` Component. Was this helpful? supported. Send",  # noqa: E501
        "Components: Font | Next.js Menu Using App Router Features available in /app App Router ... Components Font Font Module This API reference will help you understand how to use next/font/google and next/font/local . For features and usage, please see the Optimizing Fonts page. Font Function Arguments For usage, review Google Fonts and Local Fonts . Key font/google font/local Type Required src String or Array of Objects Yes weight String or Array Required/Optional style String or Array - subsets Array of Strings - axes Array of Strings - display String - preload Boolean - fallback Array of Strings - adjustFontFallback Boolean or String - variable String - declarations Array of Objects - src The path of the font file as a string or an array of objects (with type Array<path: string, weight?: string, style?: string> ) relative to the directory where the font loader function is called. Used in next/font/local Required Examples: src:'./fonts/my-font.woff2' where my-font.woff2 is placed in a directory named fonts inside the app directory src:[{path: './inter/Inter-Thin.ttf', weight: '100',},{path: './inter/Inter-Regular.ttf',weight: '400',},{path: './inter/Inter-Bold-Italic.ttf', weight: '700',style: 'italic',},] if the font loader function is called in app/page.tsx using src:'../styles/fonts/my-font.ttf' , then my-font.ttf is placed in styles/fonts at the root of the project weight The font weight with the following possibilities: A string with possible values of the weights available for the specific font or a range of values if it's a variable font An array of weight values if the font is not a variable google font . It applies to next/font/google only. Used in next/font/google and next/font/local Required if the font being used is not variable Examples: weight: '400' : A string for a single weight value - for the font Inter , the possible values are '100' , '200' , '300' , '400' , '500' , '600' , '700' , '800' , '900' or 'variable' where 'variable' is the default) weight: '100 900' : A string for the range between 100 and 900 for a variable font weight: ['100','400','900'] : An array of 3 possible values for a non variable font style The font style with the following possibilities: A string value with default value of 'normal' An array of style values if the font is not a variable google font . It applies to next/font/google only. Used in next/font/google and next/font/local Optional Examples: style: 'italic' : A string - it can be normal or italic for next/font/google style: 'oblique' : A string - it can take any value for next/font/local but is expected to come from standard font styles style: ['italic','normal'] : An array of 2 values for next/font/google - the values are from normal and italic subsets The font subsets defined by an array of string values with the names of each subset you would like to be preloaded . Fonts specified via subsets will have a link preload tag injected into the head when the preload option is true, which is the default. Used in next/font/google Optional Examples: subsets: ['latin'] : An array with the subset latin You can find a list of all subsets on the Google Fonts page for your font. axes Some variable fonts have extra axes that can be included. By default, only the font weight is included to keep the file size down. The possible values of axes depend on the specific font. Used in next/font/google Optional Examples: axes: ['slnt'] : An array with value slnt for the Inter variable font which has slnt as additional axes as shown here . You can find the possible axes values for your font by using the filter on the Google variable fonts page and looking for axes other than wght display The font display with possible string values of 'auto' , 'block' , 'swap' , 'fallback' or 'optional' with default value of 'swap' . Used in next/font/google and next/font/local Optional Examples: display: 'optional' : A string assigned to the optional value preload A boolean value that specifies whether the font should be preloaded or not. The default is true . Used in next/font/google and next/font/local Optional Examples: preload: false fallback The fallback font to use if the font cannot be loaded. An array of strings of fallback fonts with no default. Optional Used in next/font/google and next/font/local Examples: fallback: ['system-ui', 'arial'] : An array setting the fallback fonts to system-ui or arial adjustFontFallback For next/font/google : A boolean value that sets whether an automatic fallback font should be used to reduce Cumulative Layout Shift . The default is true . For next/font/local : A string or boolean false value that sets whether an automatic fallback font should be used to reduce Cumulative Layout Shift . The possible values are 'Arial' , 'Times New Roman' or false . The default is 'Arial' . Used in next/font/google and next/font/local Optional Examples: adjustFontFallback: false : for next/font/google adjustFontFallback: 'Times New Roman' : for next/font/local variable A string value to define the CSS variable name to be used if the style is applied with the CSS variable method . Used in next/font/google and next/font/local Optional Examples: variable: '--my-font' : The CSS variable --my-font is declared declarations An array of font face descriptor key-value pairs that define the generated @font-face further. Used in next/font/local Optional Examples: declarations: [{ prop: 'ascent-override', value: '90%' }] Applying Styles You can apply the font styles in three ways: className style CSS Variables className Returns a read-only CSS className for the loaded font to be passed to an HTML element. < p className = { inter .className}>Hello, Next.js!</ p > style Returns a read-only CSS style object for the loaded font to be passed to an HTML element, including style.fontFamily to access the font family name and fallback fonts. < p style = { inter .style}>Hello World</ p > CSS Variables If you would like to set your styles in an external style sheet and specify additional options there, use the CSS variable method. In addition to importing the font, also import the CSS file where the CSS variable is defined and set the variable option of the font loader object as follows: app/page.tsx import { Inter } from 'next/font/google' import styles from '../styles/component.module.css' const inter = Inter ({ variable : '--font-inter' , }) To use the font, set the className of the parent container of the text you would like to style to the font loader's variable value and the className of the text to the styles property from the external CSS file. app/page.tsx < main className = { inter .variable}> < p className = { styles .text}>Hello World</ p > </ main > Define the text selector class in the component.module.css CSS file as follows: styles/component.module.css .text { font-family : var (--font-inter) ; font-weight : 200 ; font-style : italic ; } In the example above, the text Hello World is styled using the Inter font and the generated font fallback with font-weight: 200 and font-style: italic . Using a font definitions file Every time you call the localFont or Google font function, that font will be hosted as one instance in your application. Therefore, if you need to use the same font in multiple places, you should load it in one place and import the related font object where you need it. This is done using a font definitions file. For example, create a fonts.ts file in a styles folder at the root of your app directory. Then, specify your font definitions as follows: styles/fonts.ts import { Inter , Lora , Source_Sans_3 } from 'next/font/google' import localFont from 'next/font/local' // define your variable fonts const inter = Inter () const lora = Lora () // define 2 weights of a non-variable font const sourceCodePro400 = Source_Sans_3 ({ weight : '400' }) const sourceCodePro700 = Source_Sans_3 ({ weight : '700' }) // define a custom local font where GreatVibes-Regular.ttf is stored in the styles folder const greatVibes = localFont ({ src : './GreatVibes-Regular.ttf' }) export { inter , lora , sourceCodePro400 , sourceCodePro700 , greatVibes } You can now use these definitions in your code as follows: app/page.tsx import { inter , lora , sourceCodePro700 , greatVibes } from '../styles/fonts' export default function Page () { return ( < div > < p className = { inter .className}>Hello world using Inter font</ p > < p style = { lora .style}>Hello world using Lora font</ p > < p className = { sourceCodePro700 .className}> Hello world using Source_Sans_3 font with weight 700 </ p > < p className = { greatVibes .className}>My title in Great Vibes font</ p > </ div > ) } To make it easier to access the font definitions in your code, you can define a path alias in your tsconfig.json or jsconfig.json files as follows: tsconfig.json",  # noqa: E501
    ]
    contents = [
        "Short content 1.",
        "Short content 2.",
        "Short content 3."
    ]
    optimizer = ContentSizeOptimizer(contents, max_token=3_000, max_char=999_999)

    def test_init(self):
        """初期化してインスタンスを生成できることを確認する"""
        assert type(self.optimizer) is ContentSizeOptimizer

    def test_optimize_by_token(self):
        """コンテンツのサイズを最大トークン数と最大文字数を超えないように結合したり分割したりする"""
        # コンテンツが結合されていることを確認
        joined_contents = self.optimizer.optimize_contents()
        assert len(joined_contents) == 2
        assert all([count_tokens(content) <= 3_000 for content in joined_contents])

    def test_optimize_by_char(self):
        """コンテンツのサイズを最大トークン数と最大文字数を超えないように結合したり分割したりする"""
        # コンテンツが結合されていることを確認
        optimizer = ContentSizeOptimizer(self.contents, max_token=None, max_char=10_000)
        joined_contents = optimizer.optimize_contents()
        assert len(joined_contents) == 4
        assert all([len(content) <= 10_000 for content in joined_contents])

    def test_no_optimize(self):
        """max_tokenの値がNoneの場合はコンテンツが一つに結合される"""
        optimizer = ContentSizeOptimizer(self.contents, max_token=None, max_char=None)
        joined_contents = optimizer.optimize_contents()
        assert len(joined_contents) == 1
        assert len(joined_contents[0]) > 25_000

    def test_calc_token_size(self):
        """コンテンツのトークン数を計算する"""
        assert self.optimizer.calc_total_token() == 5838

    def test_calc_char_size(self):
        """コンテンツの文字数を計算する"""
        assert self.optimizer.calc_total_char() == 27708

    def test_add_single_segment_prompt(self):
        """セグメントが一つの場合、適切なプロンプトが追加されていることを確認する"""
        optimizer = ContentSizeOptimizer(self.contents[:1], max_token=1000, max_char=10000)
        optimizer.optimize_contents()
        optimizer.add_prompts()
        expected_start = "# Prompt: Below is the complete document, consisting of a single segment.\n"
        expected_end = "\n# Prompt: Document transmission of the single segment is complete."
        assert optimizer.optimized_contents[0].startswith(expected_start)
        assert optimizer.optimized_contents[0].endswith(expected_end)

    def test_add_multiple_segments_prompts(self):
        """複数のセグメントがある場合、適切なプロンプトが各セグメントに追加されていることを確認する"""
        optimizer = ContentSizeOptimizer(self.contents, max_token=10, max_char=100)
        optimizer.optimize_contents()
        optimizer.add_prompts()

        total_segments = len(optimizer.optimized_contents)

        # 最初のセグメントのプロンプトを検証
        first_segment = optimizer.optimized_contents[0]
        expected_start_first = f"# Prompt: Beginning the document transmission. This is part 1 of {total_segments} total segments.\n"
        expected_end_first = f"\n# Prompt: End of segment 1 of {total_segments} total segments."
        assert first_segment.startswith(expected_start_first)
        assert first_segment.endswith(expected_end_first)

        # 最後のセグメントのプロンプトを検証
        last_segment = optimizer.optimized_contents[-1]
        expected_start_last = f"# Prompt: This is the final segment of the document, segment {total_segments} of {total_segments} total segments.\n"
        expected_end_last = f"\n# Prompt: End of segment {total_segments} of {total_segments} total segments."
        assert last_segment.startswith(expected_start_last)
        assert last_segment.endswith(expected_end_last)
