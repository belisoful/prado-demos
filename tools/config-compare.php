#!/usr/bin/env php
<?php
/**
 * Compare what a PRADO module or service registers from an XML configuration fragment
 * and from its PHP equivalent.
 *
 * Usage:
 *   php tools/config-compare.php <Class> <fragment.xml> <fragment.php> [<protected dir>]
 *
 *   <Class>         the module or service class, e.g. Prado\Web\Services\TJsonService
 *   <fragment.xml>  a file holding the element the loader receives: the <module> or
 *                   <service> element with its children
 *   <fragment.php>  a file that returns the array the loader receives: the module or
 *                   service entry with its 'class', 'properties' and nested keys
 *   <protected dir> the application directory TApplication is built from
 *                   (default: quickstart/protected)
 *
 * Each form runs in its own process, because an application registers once per
 * process. The child mirrors TApplication: it applies the element's attributes (XML) or
 * the 'properties' key (PHP) with setSubProperty, then calls init() with the element or
 * the entry. The parent prints both objects' properties as JSON and lists the keys that
 * differ. A TXmlElement is shown as its attributes and children, a TMap or TList as an
 * array, any other object as its class name.
 *
 * Exit status: 0 when the two forms register the same state, 1 when they differ, 2 on a
 * usage or load error.
 */

$argv0 = array_shift($argv);
$mode = null;
foreach ($argv as $i => $arg) {
    if (str_starts_with($arg, '--mode=')) {
        $mode = substr($arg, 7);
        unset($argv[$i]);
    }
}
$argv = array_values($argv);
if (count($argv) < 3) {
    fwrite(STDERR, "usage: php $argv0 <Class> <fragment.xml> <fragment.php> [<protected dir>]\n");
    exit(2);
}
[$class, $xmlFile, $phpFile] = $argv;
$protected = $argv[3] ?? 'quickstart/protected';

require __DIR__ . '/../vendor/autoload.php';

use Prado\Collections\TList;
use Prado\Collections\TMap;
use Prado\Prado;
use Prado\TApplication;
use Prado\Xml\TXmlDocument;
use Prado\Xml\TXmlElement;

function normalize(mixed $value): mixed
{
    if ($value instanceof TXmlElement) {
        $children = [];
        foreach ($value->getElements() as $child) {
            $children[] = normalize($child);
        }
        return ['<' . $value->getTagName() . '>' => $value->getAttributes()->toArray(), 'elements' => $children];
    }
    if ($value instanceof TMap || $value instanceof TList) {
        return normalize($value->toArray());
    }
    if (is_object($value)) {
        return '<' . $value::class . '>';
    }
    if (is_array($value)) {
        return array_map('normalize', $value);
    }
    return $value;
}

function dumpObject(object $object): array
{
    $out = [];
    foreach ((array) $object as $key => $value) {
        $parts = explode("\0", $key);
        $out[end($parts)] = normalize($value);
    }
    ksort($out);
    return $out;
}

if ($mode !== null) {
    // child: one configuration type per process
    $type = $mode === 'php' ? TApplication::CONFIG_TYPE_PHP : TApplication::CONFIG_TYPE_XML;
    new TApplication($protected, false, $type);
    $object = Prado::createComponent($class);
    if ($mode === 'php') {
        $entry = require $phpFile;
        if (!is_array($entry)) {
            fwrite(STDERR, "$phpFile must return an array\n");
            exit(2);
        }
        foreach ($entry['properties'] ?? [] as $name => $value) {
            $object->setSubProperty($name, $value);
        }
        unset($entry['properties']);
        $object->init($entry);
    } else {
        $document = new TXmlDocument();
        $document->loadFromFile($xmlFile);
        foreach ($document->getAttributes() as $name => $value) {
            if ($name !== 'id' && $name !== 'class') {
                $object->setSubProperty($name, $value);
            }
        }
        $object->init($document);
    }
    echo json_encode(dumpObject($object), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), "\n";
    exit(0);
}

// parent: run both forms and compare
$results = [];
foreach (['xml', 'php'] as $form) {
    $cmd = escapeshellarg(PHP_BINARY) . ' ' . escapeshellarg(__FILE__) . " --mode=$form "
        . escapeshellarg($class) . ' ' . escapeshellarg($xmlFile) . ' ' . escapeshellarg($phpFile) . ' '
        . escapeshellarg($protected) . ' 2>&1';
    $output = shell_exec($cmd);
    $decoded = json_decode((string) $output, true);
    if (!is_array($decoded)) {
        fwrite(STDERR, "[$form] did not produce a property dump:\n$output\n");
        exit(2);
    }
    $results[$form] = $decoded;
}

$keys = array_unique(array_merge(array_keys($results['xml']), array_keys($results['php'])));
sort($keys);
$differ = [];
foreach ($keys as $key) {
    $xml = json_encode($results['xml'][$key] ?? null, JSON_UNESCAPED_SLASHES);
    $php = json_encode($results['php'][$key] ?? null, JSON_UNESCAPED_SLASHES);
    $same = $xml === $php;
    if (!$same) {
        $differ[] = $key;
    }
    printf("%s %s\n    xml: %s\n    php: %s\n", $same ? '=' : '!', $key, $xml, $php);
}
echo $differ ? "\nDIFFER: " . implode(', ', $differ) . "\n" : "\nSAME\n";
exit($differ ? 1 : 0);
