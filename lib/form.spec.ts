import { IForm } from './form'
import { NPDFName as name, NPDFName } from './names'
import { Document, __mod, FontEncoding } from './document'
import { join } from 'path'
import * as tap from 'tape'
import { Font, IFont } from './painter';
import { Dictionary, IDictionary } from './dictionary'
import { Obj, IObj } from './object';

const filePath = join(__dirname, '../test-documents/test.pdf')

tap('NPDF Form Accessors and Methods', standard => {
    let doc = new Document(filePath)
    doc.on('ready', e => {
        if (e instanceof Error) {
            standard.fail(e.message)
        }
        standard.test('Form Instance Property Getters', t => {
            let acroformKeys = doc.form.dictionary.getKeys()
            t.assert(
                [name.DA, name.DR, name.FIELDS, name.SIG_FLAGS, name.XFA]
                    .every(i => acroformKeys.includes(i)),
                'AcroForm Dictionary contains all expected keys')
            t.assert((doc.form.DA as string).includes('Helv'), 'test.pdf DA should be set to Helv')
            t.assert((doc.form.DR as any) instanceof __mod.Dictionary)
            t.assert((doc.form.Fonts as Array<any>).length > 0, 'Fonts contains at least one font')
            t.assert(doc.form.needAppearances === false)
            t.end()
            global.gc()
        })
        standard.test('Creating Default Appearance', t => {
            let dr = doc.form.DR as IDictionary
            let font = doc.createFont({ fontName: 'Helvetica', encoding: FontEncoding.WinAnsi })
            let fontObj = dr.hasKey(NPDFName.FONT) ? dr.getKey(NPDFName.FONT) : null
            if (!fontObj) {
                t.fail()
            } else {
                let fontDict = Dictionary.tryGet(doc, (fontObj as IObj)) as IDictionary
                if (!fontDict) {
                    t.fail()
                } else {
                    // let f = doc.getFont('Helvetica') as IFont
                    // console.log(JSON.stringify(f.getMetrics()))
                    if (!fontDict.getKeys().includes(font.identifier)) {
                        fontDict.addKey(font.identifier, font.object)
                        t.assert(fontDict.getKeys().includes(font.identifier), 'font added to dictionary')
                        t.ok((doc.form.Fonts as Array<any>)[0].identifier, 'get font via form.Fonts')
                        let da = `0 0 0 rg /${font.identifier} ${font.size} Tf`
                        doc.form.DA = da
                        t.assert(doc.form.DA === da, 'DA set')
                        t.end()
                    }
                }
            }
            global.gc()
        })
    })
})